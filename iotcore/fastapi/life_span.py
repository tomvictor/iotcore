from contextlib import asynccontextmanager

from iotcore.broker import Broker


@asynccontextmanager
async def iotcore_broker(app):
    """FastAPI lifespan that runs an MQTT broker on port 1883 for the life of the app.

    ::

        app = FastAPI(lifespan=iotcore_broker)
    """
    broker = Broker(port=1883)
    broker.start()
    app.state.mqtt_broker = broker
    try:
        yield
    finally:
        broker.stop()
