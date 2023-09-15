from django.apps import AppConfig
from iotcore import IotCore
import os


class IotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iotcore.djangoiot"

    def ready(self):
        server_status = os.environ.get("MQTT_SERVER_RUNNING", None)
        if server_status is None:
            print("Starting MQTT server!")
            os.environ["MQTT_SERVER_RUNNING"] = "true"
            iot = IotCore()
            iot.background_loop_forever()
        else:
            print("Server already running!")
