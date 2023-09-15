from iotcore._iotcore import IotCoreRs


class Subscription(object):
    def __init__(self, topic, callback):
        self.topic = topic
        self.callback = callback

    @property
    def hash(self):
        return hash(self.topic)


class IotCore(object):
    """Create a new MQTT object

    """

    def __init__(self, host="localhost", port=1883):
        self._core = IotCoreRs(host, port, self.iot_core_callback)
        self.subscribed_topics = dict()

    def background_loop_forever(self):
        self._core.begin_subscription()

    def subscribe(self, topic, callback):
        subscription = Subscription(topic, callback)
        self.subscribed_topics[subscription.hash] = subscription
        self._core.subscribe(topic)

    def publish(self, topic, data):
        self._core.publish(topic, data)

    def iot_core_callback(self, topic, data):
        try:
            subscription = self.subscribed_topics[hash(topic)]
            subscription.callback(data)
        except KeyError:
            print(f"invalid topic : {topic}")
