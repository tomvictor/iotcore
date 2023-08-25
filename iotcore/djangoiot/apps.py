from django.apps import AppConfig
from iotcore.core import IotCore

iot_core = IotCore()


class IotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iotcore.djangoiot"

    def ready(self):
        iot_core.run()
