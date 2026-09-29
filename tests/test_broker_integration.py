"""End-to-end tests through the real Rust extension and the embedded rumqttd broker.

These need the broker ports from mqtt.toml (1883, 1884, 8083, 3030, 9042) to be free.
"""
import socket
import threading
import time

import pytest

SETTLE = 0.3  # time for SUBSCRIBE / UNSUBSCRIBE to be acknowledged by the broker
TIMEOUT = 5.0


def publish_until_received(iot, topic, payload, event):
    """Publish repeatedly until the callback fires, so a slow SUBACK cannot cause flakiness."""
    deadline = time.monotonic() + TIMEOUT
    while time.monotonic() < deadline:
        iot.publish(topic, payload)
        if event.wait(0.5):
            return True
    return False


def test_extension_module_exports_expected_classes():
    from iotcore import iotcore as ext
    import iotcore

    assert {"IotCoreRs", "IotCoreBroker"} <= set(dir(ext))
    assert iotcore.IotCoreBroker is ext.IotCoreBroker
    assert hasattr(ext.IotCoreRs, "unsubscribe")


def test_embedded_broker_is_listening_on_1883(iot):
    with socket.create_connection(("127.0.0.1", 1883), timeout=TIMEOUT):
        pass


def test_publish_subscribe_roundtrip(iot):
    got = []
    event = threading.Event()

    def on_message(data):
        got.append(data)
        event.set()

    iot.subscribe("it/roundtrip", on_message)
    time.sleep(SETTLE)

    assert publish_until_received(iot, "it/roundtrip", "hello", event)
    assert got[0] == "hello"
    assert isinstance(got[0], str)


def test_messages_are_dispatched_to_matching_callback(iot):
    got_a, got_b = [], []
    event_a, event_b = threading.Event(), threading.Event()

    def on_a(data):
        got_a.append(data)
        event_a.set()

    def on_b(data):
        got_b.append(data)
        event_b.set()

    iot.subscribe("it/dispatch/a", on_a)
    iot.subscribe("it/dispatch/b", on_b)
    time.sleep(SETTLE)

    assert publish_until_received(iot, "it/dispatch/a", "for-a", event_a)
    assert publish_until_received(iot, "it/dispatch/b", "for-b", event_b)
    assert got_a == ["for-a"] * len(got_a)  # only messages for topic a
    assert got_b == ["for-b"] * len(got_b)
    assert "for-b" not in got_a and "for-a" not in got_b


def test_unsubscribe_stops_delivery(iot):
    got = []
    event = threading.Event()

    def on_message(data):
        got.append(data)
        event.set()

    iot.subscribe("it/unsub", on_message)
    time.sleep(SETTLE)
    assert publish_until_received(iot, "it/unsub", "before", event)

    iot.unsubscribe("it/unsub")
    time.sleep(SETTLE)
    got.clear()
    event.clear()

    iot.publish("it/unsub", "after")
    assert not event.wait(1.0)
    assert got == []


def test_resubscribe_after_unsubscribe_works(iot):
    got = []
    event = threading.Event()

    def on_message(data):
        got.append(data)
        event.set()

    iot.subscribe("it/resub", on_message)
    time.sleep(SETTLE)
    iot.unsubscribe("it/resub")
    time.sleep(SETTLE)
    iot.subscribe("it/resub", on_message)
    time.sleep(SETTLE)

    assert publish_until_received(iot, "it/resub", "again", event)
    assert got[0] == "again"


def test_accept_decorator_receives_messages(iot):
    got = []
    event = threading.Event()

    @iot.accept(topic="it/decorated")
    def handler(data):
        got.append(data)
        event.set()

    time.sleep(SETTLE)
    assert publish_until_received(iot, "it/decorated", "{'temp': 18}", event)
    assert got[0] == "{'temp': 18}"
