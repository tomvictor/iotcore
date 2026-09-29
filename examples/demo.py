"""Minimal standalone demo: start the embedded broker, subscribe, publish, unsubscribe.

Run from the repository root (the broker reads mqtt.toml from the working directory):

    python examples/demo.py
"""
import time

from iotcore import IotCore


def on_temperature(data):
    print(f"temperature > {data}")


def main():
    iot = IotCore()  # starts the broker on localhost:1883 if nothing is listening there
    iot.background_loop_forever()

    iot.subscribe("temperature", on_temperature)
    time.sleep(0.5)

    iot.publish("temperature", "{'temp': 18}")
    time.sleep(0.5)

    iot.unsubscribe("temperature")
    iot.publish("temperature", "not delivered, we unsubscribed")
    time.sleep(0.5)


if __name__ == "__main__":
    main()
