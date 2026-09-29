import os
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def iot():
    """A single shared IotCore instance backed by the embedded broker.

    The Rust side reads ``mqtt.toml`` from the current working directory, so the
    fixture changes into the repository root first. The instance is session scoped
    because every IotCore connects with the same hard-coded MQTT client id and a
    second connection would kick the first one off the broker.
    """
    os.chdir(REPO_ROOT)
    from iotcore import IotCore

    core = IotCore()
    core.background_loop_forever()
    return core
