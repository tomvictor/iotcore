from django.apps import AppConfig
import subprocess
import os


def get_goiot_executable_path():
    # Get the path of the current file
    current_file_path = os.path.abspath(__file__)

    # Append the "goiot" executable filename to the current file path
    goiot_executable_path = os.path.join(os.path.dirname(current_file_path), "iot")

    return goiot_executable_path


class IotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangoiot"

    def ready(self):
        subprocess.Popen(["pwd"])
        print(get_goiot_executable_path())
        subprocess.Popen([get_goiot_executable_path()])
