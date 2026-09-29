mod broker;
mod core;

use pyo3::prelude::*;

/// Native extension behind the `iotcore` Python package.
///
/// `IotCoreRs` is the MQTT client and `IotCoreBroker` the embedded rumqttd broker.
/// Both are wrapped by the friendlier classes in `iotcore/mqtt.py` and `iotcore/broker.py`.
#[pymodule]
mod iotcore {
    use pyo3::prelude::*;

    #[pymodule_export]
    use super::broker::IotCoreBroker;
    #[pymodule_export]
    use super::core::IotCoreRs;

    #[pymodule_init]
    fn init(_m: &Bound<'_, PyModule>) -> PyResult<()> {
        // Route Rust `log`/`tracing` output into Python's `logging` module ("iotcore.*" loggers).
        let _ = pyo3_log::try_init();
        Ok(())
    }
}
