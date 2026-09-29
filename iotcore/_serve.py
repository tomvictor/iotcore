"""Private entry point of the broker child process started by :class:`iotcore.Broker`.

Started by ``Broker.start()`` with the JSON options as the first argument.

The parent keeps our stdin open; when it closes (parent exited or called stop()), we exit.
"""
import json
import logging
import os
import sys
import threading

from iotcore.iotcore import IotCoreBroker


def _exit_when_parent_goes_away() -> None:
    try:
        sys.stdin.buffer.read()  # blocks until the parent's end of the pipe closes
    finally:
        os._exit(0)


def main() -> None:
    options = json.loads(sys.argv[1])
    config_path = options.pop("config_path", None)
    level = os.environ.get("IOTCORE_LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # rumqttd wraps its per-message routing in `error_span!`s, so its tracing output shows up
    # as ERROR records for every packet. Only let it through when explicitly debugging.
    logging.getLogger("rumqttd").setLevel(logging.DEBUG if level == "DEBUG" else logging.CRITICAL)
    threading.Thread(target=_exit_when_parent_goes_away, daemon=True).start()
    IotCoreBroker(config_path=config_path, **options).run_forever()


if __name__ == "__main__":
    main()
