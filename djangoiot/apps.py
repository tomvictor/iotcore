from django.apps import AppConfig
import subprocess
import os
import psutil


# TODO: read it from settings
GO_BINARY = "goiotbackend"


def get_iot_executable_path():
    # Get the path of the current file
    current_file_path = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(current_file_path), GO_BINARY)


def is_process_running(process_name):
    for process in psutil.process_iter(attrs=['name']):
        if process.name() == process_name:
            return True
    return False


def run_iot_backend():
    if is_process_running(GO_BINARY):
        print("Go process already running!")
    else:
        subprocess.Popen(["pwd"])
        print("Starting Go process...")
        subprocess.Popen([get_iot_executable_path()])


class IotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangoiot"

    def ready(self):
        run_iot_backend()
