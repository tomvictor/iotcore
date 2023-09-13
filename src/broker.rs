use pyo3::prelude::*;
use std::thread;
use rumqttd::{Broker, Config};
use std::str;

#[pyclass]
pub struct IotCoreBroker {
    name: String,
}

impl IotCoreBroker {
    fn new(name: &str) -> Self {
        let name = String::from(name);
        Self { name }
    }
    fn run_forever() -> PyResult<()> {
        println!("Starting Iot Broker!");
        let config = config::Config::builder()
            .add_source(config::File::with_name("mqtt.toml"))
            .build()
            .unwrap();

        let config: Config = config.try_deserialize().unwrap();

        dbg!(&config);
        let mut broker = Broker::new(config);

        thread::spawn(move || {
            broker.start().unwrap()
        });

        Ok(())
    }
}