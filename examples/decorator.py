class IoTCore:
    def __init__(self):
        self.subs = {}  # Dictionary to store topic-callback function pairs

    def accept(self, topic):
        def decorator(func):
            self.subs[topic] = func  # Store the topic and callback function in the dictionary

            def wrapper(request):
                func(request)

            return wrapper

        return decorator

    def temp(self):
        print("do something")


iot = IoTCore()


@iot.accept(topic="request/temperature/data")
def temperature_data_handler(request):
    print("Handling temperature data request:", request)


# Simulate a temperature data request
request_data = {
    'topic': 'request/temperature/data',
    'data': {
        'temperature': 25.5
    }
}


def main():
    temperature_data_handler(request_data)
    iot.temp()


if __name__ == "__main__":
    main()
