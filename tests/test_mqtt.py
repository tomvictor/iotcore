"""Unit tests for the pure-Python wrapper in iotcore/mqtt.py.

The Rust extension is replaced with a fake so these run instantly and without a broker.
"""
import pytest

import iotcore.mqtt as mqtt_module
from iotcore.mqtt import IotCore, Subscription


class FakeCore:
    """Stand-in for the Rust ``IotCoreRs`` class that records every call."""

    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.callback = callback
        self.calls = []

    def subscribe(self, topic):
        self.calls.append(("subscribe", topic))

    def unsubscribe(self, topic):
        self.calls.append(("unsubscribe", topic))

    def publish(self, topic, data):
        self.calls.append(("publish", topic, data))

    def begin_subscription(self):
        self.calls.append(("begin_subscription",))


@pytest.fixture
def iot(monkeypatch):
    monkeypatch.setattr(mqtt_module, "IotCoreRs", FakeCore)
    return IotCore(host="broker.example", port=1234)


def test_constructor_forwards_host_port_and_callback(iot):
    assert iot._core.host == "broker.example"
    assert iot._core.port == 1234
    assert iot._core.callback == iot.iot_core_callback
    assert iot.subscribed_topics == {}
    assert iot.convert_to_str is True


def test_subscription_hash_is_topic_hash():
    sub = Subscription("a/b", lambda data: None)
    assert sub.hash == hash("a/b")


def test_subscribe_registers_topic_and_forwards_to_core(iot):
    cb = lambda data: None  # noqa: E731
    iot.subscribe("sensors/temp", cb)

    assert iot.subscribed_topics[hash("sensors/temp")].callback is cb
    assert iot._core.calls == [("subscribe", "sensors/temp")]


def test_unsubscribe_removes_topic_and_forwards_to_core(iot):
    iot.subscribe("sensors/temp", lambda data: None)
    iot.unsubscribe("sensors/temp")

    assert iot.subscribed_topics == {}
    assert iot._core.calls == [("subscribe", "sensors/temp"), ("unsubscribe", "sensors/temp")]


def test_unsubscribe_unknown_topic_is_a_noop(iot):
    iot.unsubscribe("never/subscribed")

    assert iot.subscribed_topics == {}
    assert iot._core.calls == []


def test_unsubscribe_only_affects_named_topic(iot):
    iot.subscribe("a", lambda data: None)
    iot.subscribe("b", lambda data: None)
    iot.unsubscribe("a")

    assert list(iot.subscribed_topics) == [hash("b")]


def test_publish_forwards_to_core(iot):
    iot.publish("sensors/temp", "21.5")

    assert iot._core.calls == [("publish", "sensors/temp", "21.5")]


def test_background_loop_forever_starts_subscription_loop(iot):
    iot.background_loop_forever()

    assert iot._core.calls == [("begin_subscription",)]


def test_callback_decodes_bytes_to_str_by_default(iot):
    received = []
    iot.subscribe("t", received.append)

    iot.iot_core_callback("t", list(b"h\xc3\xa9llo"))

    assert received == ["héllo"]


def test_callback_passes_raw_payload_when_convert_disabled(monkeypatch):
    monkeypatch.setattr(mqtt_module, "IotCoreRs", FakeCore)
    iot = IotCore(convert_to_str=False)
    received = []
    iot.subscribe("t", received.append)

    payload = [1, 2, 3]
    iot.iot_core_callback("t", payload)

    assert received == [payload]


def test_callback_for_unknown_topic_does_not_raise(iot, capsys):
    iot.iot_core_callback("unknown", list(b"x"))

    assert "invalid topic : unknown" in capsys.readouterr().out


def test_callback_after_unsubscribe_is_ignored(iot):
    received = []
    iot.subscribe("t", received.append)
    iot.unsubscribe("t")

    iot.iot_core_callback("t", list(b"late"))

    assert received == []


def test_accept_decorator_subscribes_function(iot):
    received = []

    @iot.accept(topic="temperature")
    def handler(data):
        received.append(data)

    assert iot._core.calls == [("subscribe", "temperature")]
    iot.iot_core_callback("temperature", list(b"18"))
    assert received == ["18"]
    # the decorated function itself stays callable
    handler("direct")
    assert received == ["18", "direct"]
