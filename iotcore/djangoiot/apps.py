from django.apps import AppConfig
from iotcore import IotCore
import os


class IotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iotcore.djangoiot"
    iotcore_instance = None

    def ready(self):
        server_status = os.environ.get("MQTT_SERVER_RUNNING", None)
        if server_status is None:
            print("Starting MQTT server!")
            os.environ["MQTT_SERVER_RUNNING"] = "true"
            self.iotcore_instance = IotCore()
            self.iotcore_instance.background_loop_forever()
        else:
            print("Server already running!")
