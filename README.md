# iotcore - MQTT and IoT capabilities to Django Rest Framework and FastAPI.


Project under development. Apis can change often until stable.

## Planned Features

* MQTT based IoT protocol 
* MQTT broker with websocket and tcp support (Written in golang) 
* Easy sensor data storage 
* APIs for IoT Device management and storage 
* Most of the IoT logics will be handled by inbuilt golang application. It will then communicate with the django using channels
* and more coming soon 

## Installation

PyPI
```
pip install iotcore
```

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
cd example
pip install -r requirements.txt
python manage.py runserver
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
