use std::net::TcpListener;
use pyo3::prelude::*;
use rumqttc::{Client, MqttOptions, QoS, Event, Incoming};
use std::thread;
use std::sync::{mpsc, Arc, Mutex};
use std::str;
use bytes::Bytes;
use rumqttd::{Broker, Config};

use std::{time::Duration};

#[derive(Debug)]
pub struct Msg {
    pub topic: String,
    pub data: Bytes,
}

#[pyclass]
pub struct IotCoreRs {
    client: Client,
    callback: PyObject,
    tx: mpsc::Sender<Msg>,
    rx: Arc<Mutex<mpsc::Receiver<Msg>>>,
}


fn port_available(port: u16) -> bool {
    match TcpListener::bind(("127.0.0.1", port)) {
        Ok(_) => { true }
        Err(_) => {
            println!("Port not available");
            false
        }
    }
}

#[pymethods]
impl IotCoreRs {
    #[new]
    fn new(host: &str, port: u16, callback: PyObject) -> Self {
        let (host, port) = {
            if host == "localhost" {
                let port_status = port_available(1883);
                if port_status { start_mqtt_broker() };
                ("localhost", 1883)
            } else {
                (host, port)
            }
        };

        // wait for the broker to settle
        thread::sleep(Duration::from_secs(1));

        // create the channel
        let (tx, rx) = mpsc::channel();
        let rx_arc = Arc::new(Mutex::new(rx));

        let mqttoptions = MqttOptions::new("iotcore_client_id", host, port);
        let (client, mut connection) = Client::new(mqttoptions, 10);
        let tx_ch_clone = tx.clone();

        thread::spawn(move || {
            for notification in connection.iter() {
                match notification {
                    Ok(Event::Incoming(Incoming::Publish(publish))) => {
                        // println!("topic: {:?}", publish.topic);
                        let data = Msg {
                            topic: publish.topic,
                            data: publish.payload,
                        };
                        tx_ch_clone.send(data).expect("Failed to send payload via channels");
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


        Self { client, callback, tx, rx: rx_arc }
    }

    fn publish(&mut self, topic: &str, data: &str) -> PyResult<()> {
        let topic_to_be_subscribed = topic.to_owned();
        self.client
            .publish(topic_to_be_subscribed, QoS::AtLeastOnce, false, data)
            .unwrap();
        Ok(())
    }

    fn subscribe(&mut self, topic: &str) -> PyResult<()> {
        let topic_to_be_subscribed = topic.to_owned();
        self.client.subscribe(topic_to_be_subscribed, QoS::AtMostOnce).unwrap();
        Ok(())
    }

    fn begin_subscription(&mut self) -> PyResult<()> {
        let ref_python_callback = self.callback.clone();
        let ref_rx_channel = Arc::clone(&self.rx);

        thread::spawn(move || {
            loop {
                // Lock the mutex to access the receiver
                let received = ref_rx_channel.lock().unwrap().recv();
                if let Ok(received) = received {
                    Python::with_gil(|py| {
                        let byte_array: Vec<u8> = received.data.to_vec();
                        ref_python_callback.call1(py, (received.topic, byte_array, )).expect(
                            "Failed to call the python callback",
                        );
                    });
                } else {
                    break; // Exit the loop if the channel is closed
                }
            }
        });

        Ok(())
    }
}


pub fn start_mqtt_broker() {
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
}