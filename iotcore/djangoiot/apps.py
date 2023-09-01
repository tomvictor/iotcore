from django.apps import AppConfig
from iotcore import start_mqtt_server
import os


class IotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iotcore.djangoiot"

    def ready(self):
        server_status = os.environ.get("MQTT_SERVER_RUNNING", None)
        if server_status is None:
            print("Starting MQTT server!")
            os.environ["MQTT_SERVER_RUNNING"] = "true"
            start_mqtt_server()
        else:
            print("Server already running!")
