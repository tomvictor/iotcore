"""End-to-end tests through the real Rust client and the embedded broker."""
import asyncio
import threading
import time

import pytest

from iotcore import IotCore


SETTLE = 0.3
TIMEOUT = 5.0


def publish_until_received(publisher, topic, payload, event):
    """Publish repeatedly until the callback fires so a slow SUBACK cannot cause flakiness."""
    deadline = time.monotonic() + TIMEOUT
    while time.monotonic() < deadline:
        publisher.publish(topic, payload)
        if event.wait(0.5):
            return True
    return False


def collector():
    got, event = [], threading.Event()

    def cb(topic, data):
        got.append((topic, data))
        event.set()

    return got, event, cb


def test_publish_subscribe_roundtrip(client):
    got, event, cb = collector()
    client.subscribe("it/roundtrip", cb)
    time.sleep(SETTLE)

    assert publish_until_received(client, "it/roundtrip", "hello", event)
    assert got[0] == ("it/roundtrip", "hello")


def test_two_clients_can_coexist_and_talk(broker):
    """Regression test: 0.3.x used one hard-coded client id, so a second client kicked off the first."""
    a = IotCore(port=broker.port, start_broker=False).start()
    b = IotCore(port=broker.port, start_broker=False).start()
    try:
        assert a.client_id != b.client_id
        got, event, cb = collector()
        a.subscribe("it/pair", cb)
        time.sleep(SETTLE)

        assert publish_until_received(b, "it/pair", "from-b", event)
        assert got[0] == ("it/pair", "from-b")
    finally:
        a.stop()
        b.stop()


def test_wildcard_subscription_receives_multiple_topics(client):
    got, event, cb = collector()
    client.subscribe("it/wild/#", cb)
    time.sleep(SETTLE)

    assert publish_until_received(client, "it/wild/a", "1", event)
    event.clear()
    assert publish_until_received(client, "it/wild/b/c", "2", event)
    topics = {t for t, _ in got}
    assert {"it/wild/a", "it/wild/b/c"} <= topics


def test_unsubscribe_stops_delivery(client):
    got, event, cb = collector()
    client.subscribe("it/unsub", cb)
    time.sleep(SETTLE)
    assert publish_until_received(client, "it/unsub", "before", event)

    client.unsubscribe("it/unsub")
    time.sleep(SETTLE)
    got.clear()
    event.clear()

    client.publish("it/unsub", "after")
    assert not event.wait(1.0)
    assert got == []


def test_raw_bytes_payload(broker):
    iot = IotCore(port=broker.port, start_broker=False, convert_to_str=False).start()
    try:
        got, event, cb = collector()
        iot.subscribe("it/raw", cb)
        time.sleep(SETTLE)
        assert publish_until_received(iot, "it/raw", b"\x00\xff", event)
        assert got[0] == ("it/raw", b"\x00\xff")
    finally:
        iot.stop()


def test_async_callback_runs_on_event_loop(broker):
    got = []

    async def main():
        loop = asyncio.get_running_loop()
        done = asyncio.Event()  # created inside the loop: required on Python < 3.10

        async def cb(topic, data):
            assert asyncio.get_running_loop() is loop
            got.append(data)
            done.set()

        iot = IotCore(port=broker.port, start_broker=False)
        iot.subscribe("it/async", cb)
        iot.start()
        try:
            await asyncio.sleep(SETTLE)
            for _ in range(10):
                iot.publish("it/async", "hi")
                try:
                    await asyncio.wait_for(done.wait(), 0.5)
                    break
                except asyncio.TimeoutError:
                    pass
        finally:
            iot.stop()

    asyncio.run(main())
    assert got and got[0] == "hi"


def test_client_owns_and_stops_its_broker(broker):
    from iotcore.broker import port_in_use

    port = broker.port + 10
    iot = IotCore(port=port)
    try:
        assert iot.broker is not None and iot.broker.is_running
        assert port_in_use(port)
        # A second client on the same port reuses the running broker instead of starting one.
        other = IotCore(port=port)
        assert other.broker is None
        other.stop()
    finally:
        iot.stop()
    assert not port_in_use(port)


def test_stop_is_safe_to_call_twice(client):
    client.stop()
    client.stop()
