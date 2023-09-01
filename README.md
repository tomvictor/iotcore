# Iotcore - Python MQTT Broker and IoT Features for Django and FastAPI.

The project aims to give full support for mqtt broker and related apis. The internals of the mqtt server is  written in  
Rust using popular Tokio framework. Motive of the project is to avoid the GIL limitation of python and bring all the  fun features offered by rust.

## Features

* Full-fledged configurable Tokio based MQTT server
* No python GIL limitation
* All Standard MQTT broker features
* Zero extra setup required to run mqtt broker in you Django and Fastapi project
* and more

## Planned Features

* Device support
* Sensor support
* Sensor data storage
* Django based admin pages
* Django rest framework based APIs for managing devices and sensors
* SSL certificates and policy management

## Installation

PyPI
```
pip install iotcore
```

Create a new file called mqtt.toml in your root project directory and copy pase the sample mqtt.toml from https://github.com/tomvictor/iotcore  


# FastAPI setup

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import start_mqtt_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mqtt_server()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}

```


# Django Setup

Then add iotcore to the django apps as below in the settings.py file of your project
```python
INSTALLED_APPS = [
    "Other Apps here",
    "iotcore.djangoiot"
]
```

Now Connect to mqtt broker on localhost  
MQTT Port : 1883

# Run Example project

```shell
pip install django
pip install iotcore

python examples/django/manage.py runserver
```


For more details check the example folder

## Contribute

- Issue Tracker: github.com/tomvictor/iotcore/issues
- Source Code: github.com/tomvictor/iotcore

## Support

Star the project on GitHub :)

## License

The project is licensed under the MIT license.
