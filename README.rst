djangoiot (Under development)
=============================

.. image:: https://readthedocs.org/projects/djangoiot/badge/?version=latest
    :target: https://djangoiot.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/Tomvictor/djangoiot.svg?branch=master
    :target: https://travis-ci.org/Tomvictor/djangoiot


Djangoiot helps the Django app to effectively communicate over MQTT. Moreover,
it enables the IoT devices to communicate directly with the web apps, database
as well as algorithms.  The IoT era calls for a new connectivity protocol that
guarantees minimum data consumption and greater reliability. Therefore,
MQTT is more suitable than HTTP since it ensures complete support for actual physical devices.

Look how easy it is to use::

    from djangoiot.shortcuts import device,subscribe
    from djangoiot import broker

    new_broker = broker.register(host="localhost", port=8001)
    new_broker.subscribe("topic/hello")
    new_broker.send_message("topic/hello", "message")


For full documentation, visit `djangoiot.readthedocs.io
<https://djangoiot.readthedocs.io/en/latest/>`__.

Features
--------

- Add and configure broker
- Send message over MQTT
- Receive from MQTT broker
- Broadcast message over MQTT topics

Installation
------------

Install djangoiot by running::

    pip install djangoiot


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
