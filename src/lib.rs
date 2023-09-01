use std::net::TcpListener;
use pyo3::prelude::*;
use rumqttc::{Client,Connection, MqttOptions, QoS, Event, Incoming};
use std::thread;
use rumqttd::{Broker,Config};

#[pyclass]
struct IotCore {
    client: Client,
    connection: Connection,
    callback:PyObject,
}

#[pymethods]
impl IotCore {
    #[new]
    fn new(host: &str, port: u16, callback: PyObject,) -> Self {
        let mqttoptions = MqttOptions::new("iotcore", host, port);
        let (client,connection) = Client::new(mqttoptions, 10);
        Self { client,connection,callback }
    }

    fn log(&self, message: &str) -> PyResult<String> {
        println!("{}", message);
        Ok(message.to_string())
    }

    fn subscribe(&mut self, topic: &str) -> PyResult<()> {
        let topic = topic.to_owned();
        self.client
            .subscribe(&topic, QoS::AtLeastOnce)
            .unwrap();
        Ok(())
    }
    fn start_mqtt_server(&mut self) -> PyResult<()> {
        println!("Rust: starting mqtt server...");

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

    fn is_port_available(&mut self, port: u16) -> bool {
        match TcpListener::bind(("127.0.0.1", port)) {
            Ok(_) => {
                // Binding was successful, so the port is available.
                true
            }
            Err(_) => {
                // Binding failed, indicating the port is already in use.
                false
            }
        }
    }

    fn publish(&mut self, topic: &str,data: &str) -> PyResult<()> {
        let topic = topic.to_owned();
        let data = data.to_owned();
        self.client
            .publish(&topic, QoS::AtLeastOnce, false, data)
            .unwrap();
        Ok(())
    }


    fn run(&mut self) -> PyResult<()>{
        Python::with_gil(|py| {
            for notification in self.connection.iter() {
                match notification {
                    Ok(Event::Incoming(Incoming::Publish(publish))) => {
                        // println!("Rust > {:?}: {:?}", publish.topic,publish.payload);
                        let resp = format!("{:?}",publish.payload);
                        self.callback.call1(py, (resp, )).expect("TODO: panic message");
                    }
                    Err(e)=>{
                        println!("Error = {:?}", e);
                    }
                    others => {
                        println!("{:?}", others)
                    }
                }
            }
        });

        Ok(())
    }
}

#[pymodule]
fn _iotcore(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<IotCore>()?;
    Ok(())
}