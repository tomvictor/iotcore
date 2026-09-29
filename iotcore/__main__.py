"""Run a standalone MQTT broker: ``python -m iotcore --port 1883``."""
import argparse
import logging

from iotcore import Broker, __version__


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m iotcore", description="Run an MQTT broker.")
    parser.add_argument("--port", type=int, default=1883, help="MQTT port (default 1883)")
    parser.add_argument("--listen", default="0.0.0.0", help="bind address (default 0.0.0.0)")
    parser.add_argument("--config", help="rumqttd TOML config file; overrides --port/--listen")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--version", action="version", version=f"iotcore {__version__}")
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.log_level.upper(), format="%(levelname)s %(name)s: %(message)s")
    broker = Broker(port=args.port, listen=args.listen, config_path=args.config)
    print(f"iotcore {__version__}: MQTT broker listening on {', '.join(broker.listeners)} (Ctrl+C to stop)")
    try:
        broker.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
