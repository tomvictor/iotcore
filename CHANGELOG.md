# Changelog

## 0.4.0 (unreleased)

Breaking changes are marked with **!**.

### Added
- `iotcore.Broker`: a stoppable embedded broker with `start()`, `stop()`, context manager
  support and `listeners`. Runs rumqttd in a child process that exits with the parent.
- `python -m iotcore --port 1883 [--config mqtt.toml]` command line broker.
- `IotCore.stop()` / context manager: disconnects the client and stops a broker it started.
- Unique client id per `IotCore` instance and a `client_id=` argument. Two clients no longer
  kick each other off the broker.
- MQTT wildcard matching (`+`, `#`) for subscriptions; a message is delivered to every
  matching subscription.
- Callbacks may take `(topic, data)` as well as `(data)`, and may be `async def`.
- `publish(topic, data, qos=1, retain=False)` accepts `str` or `bytes`; `subscribe(..., qos=0)`.
- Broker options without a config file: `listen`, `port`, `max_connections`, ...
- Errors are raised as Python exceptions (`OSError` for busy ports, `ValueError` for bad
  config, `RuntimeError` for client failures) instead of aborting the process.
- Rust log output is routed to Python `logging` (`iotcore.*`, `rumqttd.*`).
- Test suite (unit, broker and end-to-end) run in CI on Linux and macOS.

### Changed
- **!** `mqtt.toml` is no longer read implicitly from the working directory. Pass
  `Broker(config_path=...)` or `IotCore(broker_config=...)`.
- **!** `IotCoreRs` callback now receives `(topic: str, payload: bytes)`; `IotCoreBroker`
  takes keyword arguments and `run_forever()` blocks. Use the `IotCore` / `Broker` wrappers.
- Callback exceptions are logged instead of crashing the delivery thread.
- `background_loop_forever()` is kept as an alias of `start()`.
- Wheels for aarch64/armv7 Linux are built on manylinux_2_28; Python 3.9+ is required.

### Removed
- `iotcore.request.Request` and the empty `iotcore.djangoiot` Django app.
- Rust-only examples (`examples/rumqttcl`, `examples/mqtt_rs`).

## 0.3.0 (2023-09-16)
- Last release of the 0.3 line. See the git history for earlier changes.
