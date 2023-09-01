from iotcore._iotcore import IotCore


def start_mqtt_server() -> None:
    def callback(payload):
        print(f"Received payload in python cb: {payload}")

    core = IotCore("", 1883, callback)
    core.start_mqtt_server()
