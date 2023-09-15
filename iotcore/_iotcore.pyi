class IotCoreRs:
    """
    IotCore main class
    """

    def __init__(self, server, port, callback) -> IotCoreRs:
        """
        Init function
        :param server: server host
        :param port: port
        :param callback: call back function
        """
        ...

    def publish(self, topic: str, data: str):
        """
        Publish date over mqtt
        :param topic: topic
        :param data: data
        :return: None
        """
        ...

    def subscribe(self, topic):
        """
        subscribe to mqtt topic
        :param topic:
        :return:
        """
        ...

    def initialize_broker(self):
        """
        Run mqtt broker
        :return: None
        """
        ...

    def begin_subscription(self):
        """
        Run mqtt broker
        :return: None
        """
        ...


class IotCoreBroker:
    """
    IotCoreBroker main class
    """

    def __init__(self, name) -> IotCoreBroker:
        """
        Init function
        :param name: server name
        """
        ...

    def run_forever(self) -> None:
        """
        Run Broker
        """
        ...
