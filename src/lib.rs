mod core;

use pyo3::prelude::*;


#[pymodule]
fn _iotcore(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<core::IotCoreRs>()?;
    Ok(())
}