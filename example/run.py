import psutil


def is_process_running(process_name):
    for process in psutil.process_iter(attrs=['name']):
        if process.name() == process_name:
            return True
    return False


if __name__ == "__main__":
    is_process_running("iot")
