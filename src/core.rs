use std::net::TcpListener;
use pyo3::prelude::*;
use rumqttc::{Client, Connection, MqttOptions, QoS, Event, Incoming};
use std::thread;
use std::time::Duration;
use rumqttd::{Broker, Config};
use std::sync::mpsc;
use std::str;
use bytes::{Bytes};



pub struct Msg {
    pub topic: String,
    pub data: Bytes,
}

#[pyclass]
pub struct _IotCore {
    client: Client,
    connection: Connection,
    callback: PyObject,
}

#[pymethods]
impl _IotCore {
    #[new]
    fn new(host: &str, port: u16, callback: PyObject) -> Self {
        let mqttoptions = MqttOptions::new("iotcore", host, port);
        let (client, connection) = Client::new(mqttoptions, 10);
        Self { client, connection, callback }
    }
    fn re_connect_to_broker(&mut self) {
        println!("Reconnecting client...");
        let mqttoptions = MqttOptions::new("iotcore", "localhost", 1883);
        let (client, connection) = Client::new(mqttoptions, 10);
        self.client = client;
        self.connection = connection;
    }

    fn initialize_broker(&mut self) -> PyResult<()> {
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

        // TODO: Add bool logic

        // self.begin_subscription().expect("Failed to begin subscription");

        // TODO: use bool logic
        self.re_connect_to_broker();

        Ok(())
    }

    fn is_port_available(&mut self, port: u16) -> bool {
        match TcpListener::bind(("127.0.0.1", port)) {
            Ok(_) => { true }
            Err(_) => { false }
        }
    }

    fn publish(&mut self, topic: &str, data: &str) -> PyResult<()> {
        println!("rust: publish");
        let topic = topic.to_owned();
        let data = data.to_owned();
        self.client
            .publish(&topic, QoS::AtLeastOnce, false, data)
            .unwrap();
        Ok(())
    }

    fn subscribe(&mut self, topic: &str) -> PyResult<()> {
        println!("rust: subscribe");
        let topic_to_be_subscribed = topic.to_owned();
        self.client
            .publish("$subscribe", QoS::AtLeastOnce, false, topic_to_be_subscribed)
            .unwrap();
        Ok(())
    }

    fn begin_subscription(&mut self) -> PyResult<()> {
        let (tx, rx) = mpsc::channel();

        thread::spawn(move || {
            // Wait for the Mqtt server to start
            thread::sleep(Duration::from_secs(2));
            let mqttoptions = MqttOptions::new("iotcore_sub", "127.0.0.1", 1883);
            let (mut client, mut connection) = Client::new(mqttoptions, 10);

            client
                .subscribe("#", QoS::AtLeastOnce)
                .unwrap();

            for notification in connection.iter() {
                match notification {
                    Ok(Event::Incoming(Incoming::Publish(publish))) => {
                        println!("topic: {:?}", publish.topic );
                        if publish.topic == "$subscribe" {
                            let topic_buf = publish.payload.clone().to_vec();
                            let topic_str = str::from_utf8(&topic_buf).unwrap();
                            println!("subscribing to {:?}",topic_str);
                            client.subscribe(topic_str,QoS::ExactlyOnce)
                                .unwrap();
                        }else {
                            println!("notification loop > {:?}: {:?}", publish.topic, publish.payload);
                            let resp = format!("{:?}", publish.payload);
                            let data = Msg {
                                topic: publish.topic,
                                data: publish.payload,
                            };
                            tx.send(data).expect("Failed to send payload via channels");
                        }
                    }
                    Err(e) => {
                        println!("Error = {:?}", e);
                    }
                    others => {
                        println!("{:?}", others)
                    }
                }
            }
        });

        let ref_python_callback = self.callback.clone();

        thread::spawn(move || {
            for received in rx {
                println!("Channel rx loop");
                Python::with_gil(|py| {
                    let byte_array: Vec<u8> = received.data.to_vec();
                    ref_python_callback.call1(py, (received.topic, byte_array, )).expect(
                        "Failed to call the python callback"
                    );
                });
            }
        });

        Ok(())
    }
}