import os
import platform
import subprocess

import psutil

from .__version__ import version


class IotCore(object):
    name = "iotcore"
    binary_prefix = "goiotbackend"

    def __init__(self, port=1883):
        self.port = port
        self.executable = self.get_executable_name()

    def already_running(self):
        for process in psutil.process_iter(attrs=['name']):
            if process.name() == self.executable:
                return True
        return False

    def run(self):
        if self.already_running():
            print("Go process already running!")
        else:
            print("Starting Go process...")
            subprocess.Popen([self.executable_path()])

    def clean(self):
        # TODO: Clean the proces
        raise NotImplementedError("clean function is not implemented")




    def executable_path(self):
        current_file_path = os.path.abspath(__file__)
        return os.path.join(os.path.dirname(current_file_path), self.executable)

    def get_executable_name(self):
        binary_map = {
            "Darwin": f"{self.binary_prefix}-mac-{version}",
            "Windows": f"{self.binary_prefix}-win-{version}.exe",
            "Linux": f"{self.binary_prefix}-linux-{version}",
        }
        return binary_map[platform.system()]
