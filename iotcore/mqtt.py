"""High-level MQTT client with optional embedded broker."""
from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any, Callable, Optional, Union

from iotcore.broker import Broker, port_in_use
from iotcore.iotcore import IotCoreRs

log = logging.getLogger("iotcore.client")

Payload = Union[str, bytes, bytearray, memoryview]


def topic_matches(topic_filter: str, topic: str) -> bool:
    """Return True if ``topic`` matches the MQTT ``topic_filter`` (supports ``+`` and ``#``)."""
    if topic_filter == topic:
        return True
    filter_parts = topic_filter.split("/")
    topic_parts = topic.split("/")
    for i, part in enumerate(filter_parts):
        if part == "#":
            # '#' must be last and matches the remainder, including an empty remainder.
            return i == len(filter_parts) - 1
        if i >= len(topic_parts):
            return False
        if part != "+" and part != topic_parts[i]:
            return False
    return len(filter_parts) == len(topic_parts)


class Subscription:
    """A topic filter bound to a callback."""

    def __init__(self, topic: str, callback: Callable[..., Any], qos: int = 0) -> None:
        self.topic = topic
        self.callback = callback
        self.qos = qos
        self.wants_topic = _positional_param_count(callback) >= 2
        self.is_async = inspect.iscoroutinefunction(callback)

    def matches(self, topic: str) -> bool:
        return topic_matches(self.topic, topic)

    def __repr__(self) -> str:
        return f"<Subscription {self.topic!r} -> {getattr(self.callback, '__name__', self.callback)!r}>"


def _positional_param_count(func: Callable[..., Any]) -> int:
    try:
        params = inspect.signature(func).parameters.values()
    except (TypeError, ValueError):
        return 1
    return sum(
        1
        for p in params
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default is p.empty
    )


class IotCore:
    """MQTT client that can bring its own broker.

    ::

        iot = IotCore()                      # broker on localhost:1883 unless one is running
        iot.subscribe("sensors/#", lambda topic, data: print(topic, data))
        iot.start()
        iot.publish("sensors/temp", "21.5")
        ...
        iot.stop()

    Callbacks take either ``(data)`` or ``(topic, data)``. ``data`` is a ``str`` unless the
    client was created with ``convert_to_str=False``, in which case it is ``bytes``.
    ``async def`` callbacks are scheduled on the event loop that was running when
    :meth:`start` was called (or the one passed to it).
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        client_id: Optional[str] = None,
        convert_to_str: bool = True,
        start_broker: bool = True,
        broker_config: Optional[str] = None,
        keep_alive: int = 5,
    ) -> None:
        self.convert_to_str = convert_to_str
        self._subscriptions: dict[str, Subscription] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._started = False
        self.broker: Optional[Broker] = None

        if start_broker and host in ("localhost", "127.0.0.1") and not port_in_use(port):
            self.broker = Broker(port=port, config_path=broker_config)
            self.broker.start()

        self._core = IotCoreRs(host, port, self._dispatch, client_id, keep_alive)

    # -- lifecycle -----------------------------------------------------------------

    @property
    def client_id(self) -> str:
        return self._core.client_id

    @property
    def subscriptions(self) -> list[Subscription]:
        return list(self._subscriptions.values())

    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> "IotCore":
        """Start delivering messages to callbacks. Returns immediately."""
        if self._started:
            return self
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
        self._loop = loop
        self._core.begin_subscription()
        self._started = True
        return self

    # kept for backwards compatibility with 0.3.x
    background_loop_forever = start

    def stop(self) -> None:
        """Disconnect from the broker and stop the embedded broker if this client started it."""
        try:
            self._core.disconnect()
        finally:
            if self.broker is not None:
                self.broker.stop()

    close = stop

    def __enter__(self) -> "IotCore":
        return self.start()

    def __exit__(self, *exc: object) -> None:
        self.stop()

    # -- messaging -----------------------------------------------------------------

    def subscribe(self, topic: str, callback: Callable[..., Any], qos: int = 0) -> None:
        """Subscribe to ``topic`` (wildcards ``+`` and ``#`` allowed)."""
        self._subscriptions[topic] = Subscription(topic, callback, qos)
        self._core.subscribe(topic, qos)

    def unsubscribe(self, topic: str) -> None:
        """Stop receiving messages for ``topic``. Unknown topics are ignored."""
        if self._subscriptions.pop(topic, None) is not None:
            self._core.unsubscribe(topic)

    def publish(self, topic: str, data: Payload, qos: int = 1, retain: bool = False) -> None:
        payload = data.encode("utf-8") if isinstance(data, str) else bytes(data)
        self._core.publish(topic, payload, qos, retain)

    def accept(self, topic: str, qos: int = 0):
        """Decorator form of :meth:`subscribe`."""

        def decorator(func):
            self.subscribe(topic, func, qos)
            return func

        return decorator

    # -- internals -----------------------------------------------------------------

    def _dispatch(self, topic: str, payload: bytes) -> None:
        """Called from the Rust callback thread for every incoming message."""
        data: Any = payload.decode("utf-8", errors="replace") if self.convert_to_str else payload
        matched = [s for s in self._subscriptions.values() if s.matches(topic)]
        if not matched:
            log.debug("no subscription matches topic %r", topic)
            return
        for sub in matched:
            args = (topic, data) if sub.wants_topic else (data,)
            try:
                if sub.is_async:
                    self._schedule_async(sub, args)
                else:
                    sub.callback(*args)
            except Exception:  # noqa: BLE001 - one bad callback must not kill the thread
                log.exception("callback for %r raised", topic)

    def _schedule_async(self, sub: Subscription, args: tuple) -> None:
        if self._loop is None or self._loop.is_closed():
            log.error(
                "async callback for %r skipped: call start() from inside a running event loop "
                "or pass loop=...",
                sub.topic,
            )
            return
        asyncio.run_coroutine_threadsafe(sub.callback(*args), self._loop)

    # kept for backwards compatibility with 0.3.x
    iot_core_callback = _dispatch
