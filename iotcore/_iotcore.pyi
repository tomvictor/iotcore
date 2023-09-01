

class IotCore:
    """
    IotCore main class
    """
    def __init__(self,server, port, callback)->IotCore:
        """
        Init function
        :param server: server host
        :param port: port
        :param callback: call back function
        """
        ...

    def publish(self,topic:str,data:str):
        """
        Publish date over mqtt
        :param topic: topic
        :param data: data
        :return: None
        """
        ...

    def subscribe(self,topic):
        """
        subscribe to mqtt topic
        :param topic:
        :return:
        """
        ...

    def run(self):
        """
        Run mqtt client
        :return: None
        """
        ...

    def start_mqtt_server(self):
        """
        Run mqtt broker
        :return: None
        """
        ...

