"""Tests for the stoppable embedded broker (iotcore.Broker)."""
import socket
import subprocess
import sys
import time

import pytest

from iotcore import Broker, IotCoreBroker
from iotcore.broker import port_in_use

PORT = 18884


def test_broker_starts_stops_and_releases_port():
    broker = Broker(port=PORT)
    assert not broker.is_running and not port_in_use(PORT)

    broker.start()
    assert broker.is_running and port_in_use(PORT)
    assert broker.listeners == [f"0.0.0.0:{PORT}"]
    assert broker.port == PORT

    broker.stop()
    assert not broker.is_running
    assert not port_in_use(PORT)
    broker.stop()  # idempotent


def test_context_manager():
    with Broker(port=PORT) as broker:
        assert broker.is_running
        with socket.create_connection(("127.0.0.1", PORT), timeout=2):
            pass
    assert not port_in_use(PORT)


def test_start_is_idempotent():
    with Broker(port=PORT) as broker:
        assert broker.start() is broker
        assert broker.is_running


def test_start_on_busy_port_raises_oserror():
    with Broker(port=PORT):
        with pytest.raises(OSError, match=str(PORT)):
            Broker(port=PORT).start()


def test_config_file_is_honoured(tmp_path):
    cfg = tmp_path / "mqtt.toml"
    cfg.write_text(
        f"""
id = 0
[router]
max_connections = 100
max_outgoing_packet_count = 200
max_segment_size = 1048576
max_segment_count = 10
[v4.1]
name = "v4-1"
listen = "127.0.0.1:{PORT + 1}"
next_connection_delay_ms = 1
    [v4.1.connections]
    connection_timeout_ms = 60000
    max_payload_size = 20480
    max_inflight_count = 100
"""
    )
    with Broker(config_path=str(cfg)) as broker:
        assert broker.listeners == [f"127.0.0.1:{PORT + 1}"]
        assert port_in_use(PORT + 1)


def test_invalid_config_raises_value_error(tmp_path):
    cfg = tmp_path / "bad.toml"
    cfg.write_text("id = 'not a number'\n")
    with pytest.raises(ValueError, match="broker config"):
        Broker(config_path=str(cfg))


def test_missing_config_raises_value_error():
    with pytest.raises(ValueError, match="cannot read"):
        IotCoreBroker(config_path="/definitely/missing.toml")


def test_invalid_listen_address_raises_value_error():
    with pytest.raises(ValueError, match="invalid listen address"):
        IotCoreBroker(listen="not-an-ip", port=PORT)


def test_child_exits_when_parent_dies(tmp_path):
    code = (
        "from iotcore import Broker; import os\n"
        f"Broker(port={PORT}).start(); os._exit(0)\n"  # exit without calling stop()
    )
    # cwd=tmp_path so the source checkout's iotcore/ directory cannot shadow the installed package
    subprocess.run([sys.executable, "-c", code], check=True, timeout=30, cwd=tmp_path)
    deadline = time.monotonic() + 5
    while port_in_use(PORT) and time.monotonic() < deadline:
        time.sleep(0.1)
    assert not port_in_use(PORT)


def test_cli_runs_a_broker(tmp_path):
    proc = subprocess.Popen(
        [sys.executable, "-m", "iotcore", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=tmp_path,
    )
    try:
        deadline = time.monotonic() + 10
        while not port_in_use(PORT) and time.monotonic() < deadline:
            assert proc.poll() is None, proc.stdout.read()
            time.sleep(0.1)
        assert port_in_use(PORT)
    finally:
        proc.terminate()
        proc.wait(5)
