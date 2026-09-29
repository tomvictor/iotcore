"""Unit tests for iotcore/mqtt.py with the Rust client replaced by a fake. No broker needed."""
import asyncio
import logging

import pytest

import iotcore.mqtt as mqtt_module
from iotcore.mqtt import IotCore, Subscription, topic_matches


class FakeCore:
    def __init__(self, host, port, callback, client_id=None, keep_alive=5):
        self.host, self.port, self.callback = host, port, callback
        self.client_id = client_id or "fake-id"
        self.calls = []

    def subscribe(self, topic, qos=0):
        self.calls.append(("subscribe", topic, qos))

    def unsubscribe(self, topic):
        self.calls.append(("unsubscribe", topic))

    def publish(self, topic, payload, qos=1, retain=False):
        self.calls.append(("publish", topic, payload, qos, retain))

    def begin_subscription(self):
        self.calls.append(("begin_subscription",))

    def disconnect(self):
        self.calls.append(("disconnect",))


@pytest.fixture
def iot(monkeypatch):
    monkeypatch.setattr(mqtt_module, "IotCoreRs", FakeCore)
    return IotCore(host="broker.example", port=1234, start_broker=False)


# -- topic matching ------------------------------------------------------------------

@pytest.mark.parametrize(
    "topic_filter, topic, expected",
    [
        ("a/b", "a/b", True),
        ("a/b", "a/c", False),
        ("a/+", "a/b", True),
        ("a/+", "a/b/c", False),
        ("+/b", "a/b", True),
        ("a/#", "a", True),
        ("a/#", "a/b/c/d", True),
        ("#", "anything/at/all", True),
        ("a/+/c", "a/b/c", True),
        ("a/+/c", "a/b/d", False),
        ("a/b", "a/b/c", False),
        ("a/b/c", "a/b", False),
    ],
)
def test_topic_matches(topic_filter, topic, expected):
    assert topic_matches(topic_filter, topic) is expected


# -- construction --------------------------------------------------------------------

def test_constructor_forwards_arguments_and_does_not_start_broker(iot):
    assert (iot._core.host, iot._core.port) == ("broker.example", 1234)
    assert iot._core.callback == iot._dispatch
    assert iot.broker is None
    assert iot.client_id == "fake-id"
    assert iot.subscriptions == []


def test_explicit_client_id_is_passed_through(monkeypatch):
    monkeypatch.setattr(mqtt_module, "IotCoreRs", FakeCore)
    iot = IotCore(client_id="my-device", start_broker=False, port=1)
    assert iot.client_id == "my-device"


def test_remote_host_never_starts_a_broker(monkeypatch):
    monkeypatch.setattr(mqtt_module, "IotCoreRs", FakeCore)
    monkeypatch.setattr(mqtt_module, "Broker", None)  # would raise if touched
    iot = IotCore(host="mqtt.example.com")
    assert iot.broker is None


# -- subscribe / unsubscribe / publish -----------------------------------------------

def test_subscribe_records_subscription_and_forwards(iot):
    cb = lambda data: None  # noqa: E731
    iot.subscribe("sensors/temp", cb, qos=1)

    assert iot.subscriptions[0].topic == "sensors/temp"
    assert iot.subscriptions[0].callback is cb
    assert iot._core.calls == [("subscribe", "sensors/temp", 1)]


def test_unsubscribe_removes_subscription_and_forwards(iot):
    iot.subscribe("sensors/temp", lambda data: None)
    iot.unsubscribe("sensors/temp")

    assert iot.subscriptions == []
    assert iot._core.calls[-1] == ("unsubscribe", "sensors/temp")


def test_unsubscribe_unknown_topic_is_a_noop(iot):
    iot.unsubscribe("never/subscribed")
    assert iot._core.calls == []


def test_publish_encodes_str_and_passes_bytes_through(iot):
    iot.publish("t", "héllo")
    iot.publish("t", b"\x00\x01", qos=2, retain=True)

    assert iot._core.calls == [
        ("publish", "t", "héllo".encode(), 1, False),
        ("publish", "t", b"\x00\x01", 2, True),
    ]


def test_start_is_idempotent_and_background_loop_forever_is_an_alias(iot):
    iot.start()
    iot.background_loop_forever()
    assert iot._core.calls == [("begin_subscription",)]


def test_stop_disconnects(iot):
    iot.stop()
    assert iot._core.calls == [("disconnect",)]


def test_context_manager_starts_and_stops(iot):
    with iot as started:
        assert started is iot
    assert iot._core.calls == [("begin_subscription",), ("disconnect",)]


# -- dispatch ------------------------------------------------------------------------

def test_dispatch_decodes_payload_and_calls_single_arg_callback(iot):
    got = []
    iot.subscribe("t", got.append)

    iot._dispatch("t", "héllo".encode())

    assert got == ["héllo"]


def test_dispatch_passes_topic_to_two_arg_callback(iot):
    got = []
    iot.subscribe("sensors/#", lambda topic, data: got.append((topic, data)))

    iot._dispatch("sensors/temp", b"21")

    assert got == [("sensors/temp", "21")]


def test_dispatch_raw_bytes_when_convert_disabled(monkeypatch):
    monkeypatch.setattr(mqtt_module, "IotCoreRs", FakeCore)
    iot = IotCore(convert_to_str=False, start_broker=False, port=1)
    got = []
    iot.subscribe("t", got.append)

    iot._dispatch("t", b"\xff\x00")

    assert got == [b"\xff\x00"]


def test_dispatch_delivers_to_every_matching_subscription(iot):
    a, b = [], []
    iot.subscribe("s/#", a.append)
    iot.subscribe("s/+", b.append)
    iot.subscribe("other", lambda d: pytest.fail("must not be called"))

    iot._dispatch("s/x", b"1")

    assert a == ["1"] and b == ["1"]


def test_dispatch_unknown_topic_is_ignored(iot, caplog):
    with caplog.at_level(logging.DEBUG, logger="iotcore.client"):
        iot._dispatch("unknown", b"x")
    assert "no subscription matches" in caplog.text


def test_dispatch_after_unsubscribe_is_ignored(iot):
    got = []
    iot.subscribe("t", got.append)
    iot.unsubscribe("t")

    iot._dispatch("t", b"late")

    assert got == []


def test_failing_callback_is_logged_not_raised(iot, caplog):
    def boom(data):
        raise ValueError("bad")

    got = []
    iot.subscribe("t", boom)
    iot.subscribe("t/#", got.append)

    with caplog.at_level(logging.ERROR, logger="iotcore.client"):
        iot._dispatch("t", b"x")

    assert "callback for 't' raised" in caplog.text
    assert got == ["x"]  # the other subscriber still got the message


def test_async_callback_is_scheduled_on_the_loop(iot):
    got = []

    async def cb(topic, data):
        got.append((topic, data))

    async def main():
        iot.subscribe("t", cb)
        iot.start()  # captures the running loop
        iot._dispatch("t", b"hi")  # simulates the Rust thread
        await asyncio.sleep(0.05)

    asyncio.run(main())
    assert got == [("t", "hi")]


def test_async_callback_without_loop_is_logged(iot, caplog):
    async def cb(data):
        pass

    iot.subscribe("t", cb)
    iot.start()  # no running loop here

    with caplog.at_level(logging.ERROR, logger="iotcore.client"):
        iot._dispatch("t", b"x")

    assert "async callback" in caplog.text


def test_accept_decorator_subscribes_and_returns_function(iot):
    @iot.accept("temperature", qos=1)
    def handler(data):
        return data

    assert iot._core.calls == [("subscribe", "temperature", 1)]
    assert handler("direct") == "direct"


def test_subscription_repr_and_matching():
    sub = Subscription("a/+", lambda d: None)
    assert sub.matches("a/b") and not sub.matches("b/a")
    assert "a/+" in repr(sub)
