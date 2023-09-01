import time

import iotcore


def callback(payload):
    print(f"Received payload in python: {payload}")


def main():
    core = iotcore.IotCore("mqtt.eclipseprojects.io", 1883, callback)
    core.publish("pub/iotcore", "hello")
    core.subscribe("sub/iotcore")
    core.run()


def develop():
    core = iotcore.IotCore("mqtt.eclipseprojects.io", 1883, callback)
    print("Python: start")
    core.start_mqtt_server()
    print("Python: end")
    time.sleep(10)


if __name__ == "__main__":
    # main()
    develop()
