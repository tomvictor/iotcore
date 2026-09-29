"""iotcore: an embedded MQTT broker and client for Python, written in Rust.

    from iotcore import IotCore

    iot = IotCore()                 # starts a broker on localhost:1883 if none is running
    iot.subscribe("sensors/#", print)
    iot.start()
    iot.publish("sensors/temp", "21.5")
"""
from importlib.metadata import PackageNotFoundError, version

from iotcore.broker import Broker
from iotcore.iotcore import IotCoreBroker, IotCoreRs
from iotcore.mqtt import IotCore, topic_matches

try:
    __version__ = version("iotcore")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "0.0.0"

__all__ = ["IotCore", "Broker", "IotCoreBroker", "IotCoreRs", "topic_matches", "__version__"]
