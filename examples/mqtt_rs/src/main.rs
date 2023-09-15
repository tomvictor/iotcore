use std::{env, process, time::Duration};
use paho_mqtt as mqtt;

fn main() {
    // Initialize the logger from the environment
    // Create a client & define connect options
    let host = "mqtt://localhost:1883".to_string();

    let mut cli = mqtt::Client::new(host).unwrap_or_else(|e| {
        println!("Error creating the client: {:?}", e);
        process::exit(1);
    });

    // Use 5sec timeouts for sync calls.
    cli.set_timeout(Duration::from_secs(5));

    let conn_opts = mqtt::ConnectOptionsBuilder::new_v3()
        .connect_timeout(Duration::from_secs(5))
        .finalize();

    if let Err(e) = cli.connect(conn_opts) {
        println!("Unable to connect: {:?}", e);
        process::exit(1);
    }

    // Create a message and publish it
    let msg = mqtt::MessageBuilder::new()
        .topic("test")
        .payload("Hello synchronous world!")
        .qos(1)
        .finalize();

    if let Err(e) = cli.publish(msg) {
        println!("Error sending message: {:?}", e);
    }

    // Disconnect from the broker
    cli.disconnect(None).unwrap();
}