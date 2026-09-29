"""Minimal standalone demo: embedded broker, subscribe, publish, unsubscribe, stop.

    python examples/demo.py
"""
import time

from iotcore import IotCore


def main():
    with IotCore() as iot:  # starts a broker on localhost:1883 if none is running

        @iot.accept("sensors/#")
        def on_sensor(topic, data):
            print(f"{topic} -> {data}")

        time.sleep(0.3)  # let the subscription settle
        iot.publish("sensors/temperature", "21.5")
        iot.publish("sensors/humidity", "40")
        time.sleep(0.3)

        iot.unsubscribe("sensors/#")
        iot.publish("sensors/temperature", "not delivered, we unsubscribed")
        time.sleep(0.3)
    # client disconnected and broker stopped here


if __name__ == "__main__":
    main()
