# djangoiot - Add MQTT and IoT capabilities to Django Rest Framework.


Project under development. Apis can change often until stable.

# Planned Features

* MQTT based IoT protocol 
* Easy sensor data storage 
* APIs for IoT Device management and storage 
* Most of the IoT logics will be handled by inbuilt golang application. It will then communicate with the django using channels

# Installation

PyPI
```
pip install djangoiot
```

Then add djangoiot to the django apps as below in the settings.py file of your project
```python
INSTALLED_APPS = [
    "Other Apps here",
    "django.contrib.staticfiles",
    "djangoiot"
]
```



MQTT Port : 1883 
Websocket Port : 1882 
Stat Port: 8080 

# Development

Use mage for development

```
mage
Targets:
  bootstrap    project
  build        djangoiot      
  clean        the builds
  dev          Clean, Build and Install dev version
  run          development django project
```



Contribute
----------

- Issue Tracker: github.com/tomvictor/djangoiot/issues
- Source Code: github.com/tomvictor/djangoiot

Support
-------

If you are having issues, please let raise issue on github.

License
-------

The project is licensed under the MIT license.
