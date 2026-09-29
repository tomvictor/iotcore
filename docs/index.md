# iotcore - an embedded MQTT broker and client for Python

[![CI](https://github.com/tomvictor/iotcore/actions/workflows/CI.yml/badge.svg)](https://github.com/tomvictor/iotcore/actions/workflows/CI.yml)
[![PyPI](https://img.shields.io/pypi/v/iotcore?color=%2334D058&label=pypi%20package)](https://pypi.org/project/iotcore)
[![Python versions](https://img.shields.io/pypi/pyversions/iotcore.svg?color=%2334D058)](https://pypi.org/project/iotcore)

**A real MQTT broker that installs with `pip` and lives inside your Python process.**

```
pip install iotcore
```

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

Point any MQTT client (mosquitto_pub, MQTTX, an ESP32) at `localhost:1883` and it talks to your app.

## Why not just run Mosquitto?

You should, if you already operate one. iotcore exists for everything before and around that:

| Situation | With Mosquitto / EMQX | With iotcore |
| --- | --- | --- |
| A Python app that needs MQTT | Install a system package or a container, manage its config and lifecycle separately | `pip install iotcore`, start it from your code, stop it with your app |
| Edge box, Raspberry Pi, kiosk, lab bench | Another service to provision, monitor and upgrade | One Python process, one deployable, one log |
| Tests for MQTT-driven code | Mock the client, or depend on a broker running on the CI machine | A pytest fixture starts a broker on a free port in ~100 ms and tears it down |
| Prototypes and workshops | "First install a broker" before anyone sees a message flow | Working in the first five minutes |
| Desktop tools, simulators, local dashboards | Ask users to run a daemon | Ships inside the tool |

The broker is [rumqttd](https://github.com/bytebeamio/rumqtt): MQTT 3.1.1 and 5, TLS, websockets,
shared subscriptions, and no Python or system dependencies. It is not a toy broker, and it is not
a pure-Python reimplementation. It is compiled into the wheel.

## Who this is for

* People shipping small IoT systems who do not want a separate message-broker deployment.
* Teams testing MQTT-based products who want an honest broker in every test, not a mock.
* Educators, makers and researchers who want MQTT working before the coffee gets cold.
* Anyone who has typed `brew install mosquitto` or `docker run eclipse-mosquitto` just to try an idea.

If you outgrow it, nothing changes in your code: point `IotCore(host=...)` at Mosquitto, EMQX or a
cloud broker and remove the embedded one.

## Features

* **Embedded broker** with `start()` / `stop()`, a context manager and a CLI (`python -m iotcore`).
* **Client** with publish, subscribe, unsubscribe, QoS 0-2, retained messages, `+` / `#` wildcards.
* **Callbacks** as plain functions or `async def` coroutines scheduled on your event loop.
* **Full rumqttd configuration** via a TOML file when you need TLS, websockets, MQTT v5 or auth.
* **Pre-built wheels** for Linux (x86_64, i686, aarch64, armv7), macOS and Windows, Python 3.9+.
* **Bring your own client**: pair `iotcore.Broker` with paho-mqtt or aiomqtt if you prefer them.

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

### In your test suite

```python
# conftest.py
import pytest
from iotcore import Broker

@pytest.fixture(scope="session")
def mqtt_broker():
    with Broker(port=18883) as broker:
        yield broker          # every test talks to a real broker on localhost:18883
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
