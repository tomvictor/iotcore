//! MQTT client: a thin wrapper around the synchronous rumqttc client.
//!
//! Incoming messages are received on a dedicated network thread and handed to a second
//! thread that invokes the Python callback, so the network loop never blocks on Python.

use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use log::{debug, error, info, warn};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rumqttc::{Client, ConnectionError, Event, Incoming, MqttOptions, Outgoing, QoS};

struct Msg {
    topic: String,
    payload: Vec<u8>,
}

static CLIENT_COUNTER: AtomicU64 = AtomicU64::new(0);

/// Build a client id that is unique per process and per client instance.
fn generate_client_id() -> String {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.subsec_nanos())
        .unwrap_or(0);
    let n = CLIENT_COUNTER.fetch_add(1, Ordering::Relaxed);
    format!("iotcore-{}-{:x}-{}", std::process::id(), nanos, n)
}

fn qos_from(qos: u8) -> PyResult<QoS> {
    match qos {
        0 => Ok(QoS::AtMostOnce),
        1 => Ok(QoS::AtLeastOnce),
        2 => Ok(QoS::ExactlyOnce),
        _ => Err(PyValueError::new_err(format!("qos must be 0, 1 or 2, got {qos}"))),
    }
}

fn to_runtime_err<E: std::fmt::Display>(e: E) -> PyErr {
    PyRuntimeError::new_err(e.to_string())
}

/// Native MQTT client. Prefer `iotcore.IotCore`, which wraps this class.
#[pyclass]
pub struct IotCoreRs {
    client: Client,
    callback: Py<PyAny>,
    client_id: String,
    rx: Mutex<Option<mpsc::Receiver<Msg>>>,
    stopped: Arc<AtomicBool>,
}

#[pymethods]
impl IotCoreRs {
    /// Connect to `host:port`. `callback(topic: str, payload: bytes)` is invoked for every
    /// incoming message once `begin_subscription()` has been called.
    #[new]
    #[pyo3(signature = (host, port, callback, client_id=None, keep_alive_secs=5))]
    fn new(
        host: &str,
        port: u16,
        callback: Py<PyAny>,
        client_id: Option<String>,
        keep_alive_secs: u64,
    ) -> PyResult<Self> {
        let client_id = client_id.unwrap_or_else(generate_client_id);
        if client_id.is_empty() {
            return Err(PyValueError::new_err("client_id must not be empty"));
        }
        let mut options = MqttOptions::new(&client_id, host, port);
        options.set_keep_alive(Duration::from_secs(keep_alive_secs.max(1)));

        let (client, mut connection) = Client::new(options, 10);
        let (tx, rx) = mpsc::channel::<Msg>();
        let stopped = Arc::new(AtomicBool::new(false));
        let stop_flag = Arc::clone(&stopped);
        let id_for_log = client_id.clone();

        thread::Builder::new()
            .name(format!("iotcore-mqtt-{client_id}"))
            .spawn(move || {
                for notification in connection.iter() {
                    match notification {
                        Ok(Event::Incoming(Incoming::Publish(publish))) => {
                            let msg = Msg {
                                topic: publish.topic,
                                payload: publish.payload.to_vec(),
                            };
                            if tx.send(msg).is_err() {
                                break; // callback side is gone
                            }
                        }
                        Ok(Event::Incoming(Incoming::ConnAck(_))) => {
                            info!("{id_for_log}: connected");
                        }
                        Ok(Event::Outgoing(Outgoing::Disconnect)) => {
                            info!("{id_for_log}: disconnected");
                            break;
                        }
                        Ok(event) => debug!("{id_for_log}: {event:?}"),
                        Err(ConnectionError::RequestsDone) => break,
                        Err(e) => {
                            if stop_flag.load(Ordering::Relaxed) {
                                break;
                            }
                            warn!("{id_for_log}: connection error ({e}), retrying");
                            thread::sleep(Duration::from_secs(1));
                        }
                    }
                }
                debug!("{id_for_log}: network thread finished");
            })
            .map_err(to_runtime_err)?;

        Ok(Self {
            client,
            callback,
            client_id,
            rx: Mutex::new(Some(rx)),
            stopped,
        })
    }

    #[getter]
    fn client_id(&self) -> &str {
        &self.client_id
    }

    /// Publish `payload` (bytes) to `topic`.
    #[pyo3(signature = (topic, payload, qos=1, retain=false))]
    fn publish(&self, topic: &str, payload: &[u8], qos: u8, retain: bool) -> PyResult<()> {
        self.client
            .publish(topic, qos_from(qos)?, retain, payload)
            .map_err(to_runtime_err)
    }

    #[pyo3(signature = (topic, qos=0))]
    fn subscribe(&self, topic: &str, qos: u8) -> PyResult<()> {
        self.client
            .subscribe(topic, qos_from(qos)?)
            .map_err(to_runtime_err)
    }

    fn unsubscribe(&self, topic: &str) -> PyResult<()> {
        self.client.unsubscribe(topic).map_err(to_runtime_err)
    }

    /// Disconnect from the broker and stop the background threads.
    fn disconnect(&self) -> PyResult<()> {
        self.stopped.store(true, Ordering::Relaxed);
        match self.client.disconnect() {
            Ok(()) => Ok(()),
            // Already disconnected: nothing to do.
            Err(rumqttc::ClientError::Request(_)) => Ok(()),
            Err(e) => Err(to_runtime_err(e)),
        }
    }

    /// Start the thread that delivers incoming messages to the Python callback.
    fn begin_subscription(&self) -> PyResult<()> {
        let rx = self
            .rx
            .lock()
            .map_err(|_| PyRuntimeError::new_err("receiver lock poisoned"))?
            .take()
            .ok_or_else(|| PyRuntimeError::new_err("begin_subscription() was already called"))?;
        let callback = self.callback.clone();
        let name = format!("iotcore-callback-{}", self.client_id);

        thread::Builder::new()
            .name(name)
            .spawn(move || {
                while let Ok(msg) = rx.recv() {
                    Python::attach(|py| {
                        let payload = PyBytes::new(py, &msg.payload);
                        if let Err(e) = callback.call1(py, (msg.topic.as_str(), payload)) {
                            error!("callback for topic '{}' raised: {e}", msg.topic);
                            e.print(py);
                        }
                    });
                }
                debug!("callback thread finished");
            })
            .map_err(to_runtime_err)?;
        Ok(())
    }
}
