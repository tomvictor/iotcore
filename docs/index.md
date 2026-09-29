# iotcore - an embedded MQTT broker and client for Python

[![CI](https://github.com/tomvictor/iotcore/actions/workflows/CI.yml/badge.svg)](https://github.com/tomvictor/iotcore/actions/workflows/CI.yml)
[![PyPI](https://img.shields.io/pypi/v/iotcore?color=%2334D058&label=pypi%20package)](https://pypi.org/project/iotcore)
[![Python versions](https://img.shields.io/pypi/pyversions/iotcore.svg?color=%2334D058)](https://pypi.org/project/iotcore)

`pip install iotcore` gives your Python application a real MQTT broker and a client, with no
external service to run and no Python dependencies. The broker is [rumqttd](https://github.com/bytebeamio/rumqtt)
and the client is rumqttc, both compiled into a native extension, so the networking runs on
Rust threads outside the GIL.

Use it when you want MQTT inside a single deployable: prototypes, edge and gateway devices, test
suites, desktop tools, or a small FastAPI / Django service that talks to a handful of devices
without standing up Mosquitto or EMQX next to it.

```python
from iotcore import IotCore

iot = IotCore()                     # starts a broker on localhost:1883 unless one is running

@iot.accept("sensors/#")            # MQTT wildcards work
def on_sensor(topic, data):
    print(topic, data)

iot.start()                         # deliver messages to callbacks in the background
iot.publish("sensors/temperature", "21.5")
...
iot.stop()                          # disconnects and shuts the broker down
```

Point any MQTT client (mosquitto_pub, MQTTX, a microcontroller) at `localhost:1883` and it will
talk to your app.

## Features

* **Embedded broker** with `start()` / `stop()`, a context manager and a CLI (`python -m iotcore`).
* **Client** with publish, subscribe, unsubscribe, QoS 0-2, retained messages, `+` / `#` wildcards.
* **Callbacks** as plain functions or `async def` coroutines scheduled on your event loop.
* **No GIL contention**: the broker and the network loop run on Rust threads.
* **Full rumqttd configuration** via a TOML file when you need TLS, websockets, MQTT v5 or auth.
* **Pre-built wheels** for Linux (x86_64, i686, aarch64, armv7), macOS and Windows, Python 3.9+.

## Installation

```
pip install iotcore
```

## Usage

### Client with embedded broker

```python
from iotcore import IotCore

iot = IotCore(host="localhost", port=1883)   # broker is started only if the port is free

def on_message(data):                        # 1-arg callbacks get the payload
    print("got", data)

def on_any(topic, data):                     # 2-arg callbacks also get the topic
    print(topic, data)

iot.subscribe("devices/+/status", on_any, qos=1)
iot.subscribe("alerts", on_message)
iot.start()

iot.publish("alerts", "overheating", qos=1, retain=False)
iot.unsubscribe("alerts")
iot.stop()
```

Payloads arrive as `str`; pass `convert_to_str=False` to get `bytes`. `publish` accepts `str` or `bytes`.
Every client gets a unique client id; pass `client_id="..."` to choose your own.

To connect to an existing broker instead, pass its host: `IotCore(host="mqtt.example.com")`.

### Broker only

```python
from iotcore import Broker

with Broker(port=1883) as broker:
    print(broker.listeners)   # ['0.0.0.0:1883']
    ...
# stopped and port released
```

From the command line:

```bash
python -m iotcore --port 1883
```

The broker runs in a child process because rumqttd has no shutdown API. It exits by itself if
your process dies. Hand it a full rumqttd TOML file for advanced setups:

```python
Broker(config_path="mqtt.toml")   # see [Broker Configuration](config.md)
```

### FastAPI

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from iotcore import IotCore

iot = IotCore()

@asynccontextmanager
async def lifespan(app: FastAPI):
    iot.start()      # called inside the event loop, so async callbacks work
    yield
    iot.stop()

app = FastAPI(lifespan=lifespan)
latest = {}

@iot.accept("sensors/#")
async def on_sensor(topic: str, data: str):
    latest[topic] = data

@app.get("/")
def home():
    return latest

@app.get("/pub")
def pub():
    iot.publish("sensors/temperature", "21.5")
    return {"published": True}
```

Only a broker, no client? `from iotcore.fastapi import iotcore_broker` and `FastAPI(lifespan=iotcore_broker)`.

### Django

```python
# views.py
from django.http import JsonResponse
from iotcore import IotCore

iot = IotCore()      # runserver's autoreloader imports this twice; the second call
iot.start()          # finds the port busy and only connects a client

@iot.accept("sensors/#")
def on_sensor(topic, data):
    print(topic, data)

def publish(request):
    iot.publish("sensors/temperature", "21.5")
    return JsonResponse({"published": True})
```

## Examples

```bash
python examples/demo.py                          # standalone script
uvicorn examples.fastapi.main:app                # FastAPI (pip install fastapi uvicorn)
python examples/django/manage.py runserver       # Django  (pip install django)
```

## Logging

Broker and client messages go to Python's `logging` under the `iotcore` and `rumqttd` loggers.
Set `IOTCORE_LOG_LEVEL=DEBUG` to see the broker process's output.

## Development

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install maturin pytest
maturin develop --release
pytest
```

See the [development guide](development.md) for the test layout,
CI and how to cut a release. Changes are listed in [the changelog](changelog.md).

## License

MIT
