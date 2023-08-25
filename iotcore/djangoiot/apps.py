from django.apps import AppConfig
from djangoiot.core import IotCore

iot_core = IotCore()


class IotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangoiot"

    def ready(self):
        iot_core.run()
