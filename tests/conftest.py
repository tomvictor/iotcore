import pytest

from iotcore import Broker, IotCore

# Integration tests use a non-default port so they never collide with a broker the
# developer may be running on 1883.
TEST_PORT = 18883


@pytest.fixture(scope="session")
def broker():
    with Broker(port=TEST_PORT) as b:
        yield b


@pytest.fixture
def client(broker):
    """A fresh, started client connected to the session broker."""
    iot = IotCore(port=TEST_PORT, start_broker=False)
    iot.start()
    yield iot
    iot.stop()
