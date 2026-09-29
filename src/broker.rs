//! Embedded MQTT broker built on rumqttd.
//!
//! rumqttd has no shutdown API: `Broker::start()` spawns OS threads and blocks forever.
//! `iotcore/broker.py` therefore runs this class in a child process so it can be stopped.

use std::collections::HashMap;
use std::net::{SocketAddr, TcpListener};
use std::thread;

use log::info;
use pyo3::exceptions::{PyOSError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use rumqttd::{Broker, Config, ConnectionSettings, RouterConfig, ServerSettings};

fn to_runtime_err<E: std::fmt::Display>(e: E) -> PyErr {
    PyRuntimeError::new_err(e.to_string())
}

fn load_config(path: &str) -> PyResult<Config> {
    let raw = config::Config::builder()
        .add_source(config::File::with_name(path))
        .build()
        .map_err(|e| PyValueError::new_err(format!("cannot read broker config '{path}': {e}")))?;
    raw.try_deserialize()
        .map_err(|e| PyValueError::new_err(format!("invalid broker config '{path}': {e}")))
}

#[allow(clippy::too_many_arguments)]
fn default_config(
    listen: &str,
    port: u16,
    max_connections: usize,
    max_payload_size: usize,
    max_inflight_count: usize,
    connection_timeout_ms: u16,
) -> PyResult<Config> {
    let listen: SocketAddr = format!("{listen}:{port}")
        .parse()
        .map_err(|e| PyValueError::new_err(format!("invalid listen address '{listen}:{port}': {e}")))?;

    let connections = ConnectionSettings {
        connection_timeout_ms,
        max_payload_size,
        max_inflight_count,
        auth: None,
        external_auth: None,
        dynamic_filters: true,
    };
    let server = ServerSettings {
        name: "v4-1".to_string(),
        listen,
        tls: None,
        next_connection_delay_ms: 1,
        connections,
    };
    let router = RouterConfig {
        max_connections,
        max_outgoing_packet_count: 200,
        max_segment_size: 104_857_600,
        max_segment_count: 10,
        custom_segment: None,
        initialized_filters: None,
        shared_subscriptions_strategy: Default::default(),
    };
    let mut v4 = HashMap::new();
    v4.insert("1".to_string(), server);

    Ok(Config {
        id: 0,
        router,
        v4: Some(v4),
        ..Default::default()
    })
}

fn listen_addresses(config: &Config) -> Vec<String> {
    let mut out = Vec::new();
    for group in [&config.v4, &config.v5, &config.ws].into_iter().flatten() {
        for server in group.values() {
            out.push(server.listen.to_string());
        }
    }
    out
}

/// Embedded MQTT broker. Prefer `iotcore.Broker`, which runs this in a stoppable child process.
#[pyclass]
pub struct IotCoreBroker {
    config: Config,
}

#[pymethods]
impl IotCoreBroker {
    /// Create a broker either from a rumqttd TOML file (`config_path`) or from the keyword
    /// arguments, which configure a single plain MQTT v4 listener.
    #[new]
    #[pyo3(signature = (
        config_path=None,
        listen="0.0.0.0",
        port=1883,
        max_connections=10_000,
        max_payload_size=20_480,
        max_inflight_count=100,
        connection_timeout_ms=60_000,
    ))]
    fn new(
        config_path: Option<&str>,
        listen: &str,
        port: u16,
        max_connections: usize,
        max_payload_size: usize,
        max_inflight_count: usize,
        connection_timeout_ms: u16,
    ) -> PyResult<Self> {
        let config = match config_path {
            Some(path) => load_config(path)?,
            None => default_config(
                listen,
                port,
                max_connections,
                max_payload_size,
                max_inflight_count,
                connection_timeout_ms,
            )?,
        };
        if listen_addresses(&config).is_empty() {
            return Err(PyValueError::new_err(
                "broker config defines no v4, v5 or websocket listener",
            ));
        }
        Ok(Self { config })
    }

    /// All `host:port` addresses the broker will listen on.
    fn listeners(&self) -> Vec<String> {
        listen_addresses(&self.config)
    }

    /// Raise `OSError` if any listener address is already in use.
    fn check_ports(&self) -> PyResult<()> {
        for addr in listen_addresses(&self.config) {
            TcpListener::bind(&addr)
                .map_err(|e| PyOSError::new_err(format!("cannot listen on {addr}: {e}")))?;
        }
        Ok(())
    }

    /// Run the broker on the calling thread. Blocks until the process exits.
    fn run_forever(&self, py: Python<'_>) -> PyResult<()> {
        self.check_ports()?;
        let mut broker = Broker::new(self.config.clone());
        info!("broker listening on {}", self.listeners().join(", "));
        py.detach(move || broker.start()).map_err(to_runtime_err)
    }

    /// Run the broker on background threads and return immediately.
    /// Note: an in-process broker cannot be stopped; use `iotcore.Broker` for that.
    fn start(&self) -> PyResult<()> {
        self.check_ports()?;
        let mut broker = Broker::new(self.config.clone());
        info!("broker listening on {}", self.listeners().join(", "));
        thread::Builder::new()
            .name("iotcore-broker".to_string())
            .spawn(move || {
                if let Err(e) = broker.start() {
                    log::error!("broker stopped: {e}");
                }
            })
            .map_err(to_runtime_err)?;
        Ok(())
    }
}
