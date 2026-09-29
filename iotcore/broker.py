"""A stoppable embedded MQTT broker.

The Rust broker (rumqttd) has no shutdown API, so :class:`Broker` runs it in a child
process (``python -m iotcore._serve``). ``stop()`` terminates that process, which releases
the listening ports, and the child exits by itself if the parent process goes away.
"""
from __future__ import annotations

import atexit
import json
import logging
import socket
import subprocess
import sys
import time
from typing import Any, Optional

from iotcore.iotcore import IotCoreBroker

log = logging.getLogger("iotcore.broker")

_READY_POLL = 0.05

# `python -c` puts the working directory first on sys.path; drop it so a directory named
# `iotcore` in the user's project (or this repo's source tree) cannot shadow the package.
_CHILD_BOOTSTRAP = (
    "import sys; sys.path[:] = [p for p in sys.path if p not in ('', '.')]; "
    "from iotcore._serve import main; main()"
)


def port_in_use(port: int, host: str = "127.0.0.1", timeout: float = 0.2) -> bool:
    """Return True if something accepts TCP connections on ``host:port``."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _connect_host(listen_host: str) -> str:
    """Host to connect to when checking a listener bound to ``listen_host``."""
    return "127.0.0.1" if listen_host in ("0.0.0.0", "", "::") else listen_host


class Broker:
    """Embedded MQTT broker running in a child process.

    ::

        with Broker(port=1883) as broker:
            ...                      # broker is listening
        # stopped and ports released here

    Configure a plain MQTT listener with keyword arguments, or hand a full rumqttd TOML
    file via ``config_path`` (see the *Broker Configuration* page) for TLS, websockets,
    MQTT v5 or authentication.
    """

    def __init__(
        self,
        port: int = 1883,
        listen: str = "0.0.0.0",
        config_path: Optional[str] = None,
        **options: Any,
    ) -> None:
        self.config_path = config_path
        self.options = {"listen": listen, "port": port, **options}
        self._native = IotCoreBroker(config_path=config_path, **self.options)
        self._process: Optional[subprocess.Popen] = None

    @property
    def listeners(self) -> list[str]:
        """All ``host:port`` addresses the broker listens on."""
        return list(self._native.listeners())

    @property
    def port(self) -> int:
        return int(self.listeners[0].rsplit(":", 1)[1])

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self, timeout: float = 10.0) -> "Broker":
        """Start the broker and block until it accepts connections.

        Raises ``OSError`` if a listener port is already in use and ``RuntimeError``
        if the broker does not come up within ``timeout`` seconds.
        """
        if self.is_running:
            return self
        self._native.check_ports()

        options = json.dumps({"config_path": self.config_path, **self.options})
        self._process = subprocess.Popen(
            [sys.executable, "-c", _CHILD_BOOTSTRAP, options],
            stdin=subprocess.PIPE,  # the child exits when this pipe closes
        )
        atexit.register(self.stop)

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            code = self._process.poll()
            if code is not None:
                self._process = None
                raise RuntimeError(f"broker process exited with code {code} during startup")
            if all(self._listener_ready(addr) for addr in self.listeners):
                log.info("broker listening on %s", ", ".join(self.listeners))
                return self
            time.sleep(_READY_POLL)

        self.stop()
        raise RuntimeError(f"broker did not start listening within {timeout}s")

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the broker process and release its ports. Safe to call twice."""
        process = self._process
        if process is None:
            return
        self._process = None
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout)
        if process.stdin is not None:
            process.stdin.close()
        log.info("broker stopped")

    def run_forever(self) -> None:
        """Run the broker in *this* process and block until interrupted (used by the CLI)."""
        self._native.run_forever()

    def __enter__(self) -> "Broker":
        return self.start()

    def __exit__(self, *exc: object) -> None:
        self.stop()

    def __repr__(self) -> str:
        state = "running" if self.is_running else "stopped"
        return f"<Broker {', '.join(self.listeners)} {state}>"

    @staticmethod
    def _listener_ready(addr: str) -> bool:
        host, port = addr.rsplit(":", 1)
        return port_in_use(int(port), _connect_host(host))
