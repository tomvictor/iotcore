djangoiot
=========

djangoiot help django app to communicate over MQTT. This will enable IoT
devices to talk directly to a web apps, database and algorithms. This will help IoT perfectionists
to forgive HTTP and still use hardware with 4KB RAM.

Look how easy it is to use::

    from djangoiot.shortcuts import device,subscribe
    from djangoiot import broker

    new_broker = broker.register(host="localhost", port=8001)
    new_broker.subscribe("topic/hello")
    new_broker.send_message("topic/hello", "message")


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

The project is licensed under the BSD license.
