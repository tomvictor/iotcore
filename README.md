# Iotcore - Python MQTT Broker and IoT Features for Django and FastAPI

[![.github/workflows/CI.yml](https://github.com/tomvictor/iotcore/actions/workflows/CI.yml/badge.svg)](https://github.com/tomvictor/iotcore/actions/workflows/CI.yml)
[![](https://img.shields.io/pypi/v/iotcore?color=%2334D058&label=pypi%20package)](https://pypi.org/project/iotcore)
[![](https://img.shields.io/pypi/pyversions/fastapi.svg?color=%2334D058)](https://pypi.org/project/iotcore)

The project aims to give full support for mqtt broker and related apis. The internals of the mqtt server is  written in  
Rust using popular Tokio framework. Motive of the project is to avoid the GIL limitation of python and bring all the  fun features offered by rust.

## Features

* Full-fledged configurable Tokio based MQTT broker
* No python GIL limitation
* All Standard MQTT broker features
* Zero extra setup required to run mqtt broker in you Django and Fastapi project
* MQTT client, with callback support for async or non-blocking applications
* and more

## Planned Features

* Device support
* Sensor support
* Sensor data storage
* Django based admin pages
* Django rest framework based APIs for managing devices and sensors
* SSL certificates and policy management

## Installation

```
pip install iotcore
```

Create a new file called mqtt.toml in your root project directory and copy pase the sample mqtt.toml from
https://tomvictor.github.io/iotcore/config/


## FastAPI setup

**Broker only**

```python
from fastapi import FastAPI
from iotcore.fastapi import iotcore_broker

app = FastAPI(lifespan=iotcore_broker)


@app.get("/")
def read_root():
    return {"Hello": "World"}

```

**Broker plus Mqtt client**

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore

iot = IotCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    iot.background_loop_forever()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"Hello": "World"}


def mqtt_callback(data):
    print(f"iot >: {data}")


@app.get("/sub")
def sub():
    iot.subscribe("iot", mqtt_callback)
    return {"response": "subscribed"}


@app.get("/pub")
def pub():
    iot.publish("iot", "test")
    return {"response": "published"}



```


## Django Setup

Then add iotcore to the django apps as below in the settings.py file of your project
```python
from django.http import JsonResponse
from iotcore import IotCore

iot = IotCore()
iot.background_loop_forever()


def mqtt_callback(data):
    print(f"Django >: {data}")


def subscribe(request):
    iot.subscribe("iot", mqtt_callback)
    return JsonResponse({"response": "subscribed"})


def publish(request):
    iot.publish("iot", "demo")
    return JsonResponse({"response": "published"})
```

Now Connect to mqtt broker on localhost  
MQTT Port : 1883

## Run Example project


**Django**

```shell
pip install iotcore
pip install django

python examples/django/manage.py runserver
```

**FastAPI**

```shell
pip install iotcore
pip install fastapi
pip install uvicorn

uvicorn examples.fastapi.main:app
```

Open you mqtt client and use below details to connect to the broker:  
**_Host_**: **127.0.0.1** or  **localhost**  
**_Port_**: **1883**

## Contribute

- Issue Tracker: github.com/tomvictor/iotcore/issues
- Source Code: github.com/tomvictor/iotcore

## Support

Star the project on GitHub :)

## License

The project is licensed under the MIT license.
