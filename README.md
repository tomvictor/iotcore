# Iotcore - MQTT and IoT capabilities to Django Rest Framework and FastAPI.

The project aims to give full support for mqtt based server and related apis. The internals of the mqtt server is
written in golang. The python will not directly interact with the golang instead communicate using grpc(planned). The 
motive is to avoid the GIL limitation of python and bring all the  fun features offered by golang.

## Planned Features

* Full fledged MQTT server
* with websocket and tcp support (Written in golang)
* MQTT v5 support
* and more coming soon

## Installation

PyPI
```
pip install iotcore
```

# FastAPI setup

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore

iot_core = IotCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    iot_core.run()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}

```

Output

```shell
❯ cd examples/fastapi
❯ uvicorn main:app
INFO:     Started server process [62593]
INFO:     Waiting for application startup.
Starting Go process...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
11:21PM INF added hook hook=allow-all-auth
11:21PM INF attached listener address=:1883 id=t1 protocol=tcp
11:21PM INF attached listener address=:1882 id=ws1 protocol=ws
11:21PM INF attached listener address=:8080 id=stats protocol=http
11:21PM INF mochi mqtt starting version=2.3.0
11:21PM INF mochi mqtt server started

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
Websocket Port : 1882  
Stat Port: 8080  

# Run Example project

```shell
pip install -r requirements.txt
python examples/manage.py runserver
```
Output

```shell
System check identified no issues (0 silenced).
August 25, 2023 - 07:14:33
Django version 4.2.4, using settings 'develop.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

Starting golang
7:14AM INF added hook hook=allow-all-auth
7:14AM INF attached listener address=:1883 id=t1 protocol=tcp
7:14AM INF attached listener address=:1882 id=ws1 protocol=ws
7:14AM INF attached listener address=:8080 id=stats protocol=http
7:14AM INF mochi mqtt starting version=2.3.0
7:14AM INF mochi mqtt server started

```

For more details check the example folder

## Development

Use mage for development

```shell
mage
Targets:
  bootstrap    project
  build        iotcore      
  clean        the builds
  dev          Clean, Build and Install dev version
  run          development django project
```



## Contribute

- Issue Tracker: github.com/tomvictor/iotcore/issues
- Source Code: github.com/tomvictor/iotcore

## Support

If you are having issues, please let raise issue on github.

## License

The project is licensed under the MIT license.
