# Development & Testing

Iotcore is a mixed Rust / Python project. The MQTT broker and client live in `src/` and are
compiled into the extension module `iotcore.iotcore` with [maturin](https://www.maturin.rs/).
The public API lives in `iotcore/mqtt.py` (`IotCore`) and `iotcore/broker.py` (`Broker`).
`iotcore/_serve.py` is the entry point of the broker child process.

## Prerequisites

* Python 3.9 or newer
* A stable Rust toolchain (`rustup`)
* [`uv`](https://docs.astral.sh/uv/) or plain `pip`

## Build from source

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install maturin pytest
maturin develop --release
```

`maturin develop` compiles the Rust crate and installs `iotcore` into the active virtualenv in
editable mode. Re-run it after every change to the Rust sources; changes to the Python files are
picked up immediately.

To build distributable wheels instead:

```bash
maturin build --release --out dist --find-interpreter
```

## Run the tests

```bash
pytest
```

The test suite has two layers:

| File | What it covers | Needs |
| --- | --- | --- |
| `tests/test_mqtt.py` | The Python wrapper (`IotCore`): topic matching, subscribe/unsubscribe/publish, callback dispatch (sync and async), the `@accept` decorator. The Rust client is replaced with a fake. | nothing |
| `tests/test_broker.py` | `Broker` lifecycle: start/stop, port release, busy ports, config files, orphan cleanup and the CLI. | free ports 18884-18885 |
| `tests/test_integration.py` | Round trips through the real Rust client and broker: delivery, wildcards, unsubscribe, two clients side by side, raw bytes, async callbacks, client-owned broker. | free ports 18883 and 18893 |

The suite never touches port 1883, so it runs alongside a broker you may have running.

## Continuous integration

`.github/workflows/CI.yml` runs on every push and pull request:

* **test** builds the extension natively on Linux and macOS for Python 3.9 and 3.13 and runs `pytest`.
* **linux / windows / macos / sdist** build release wheels for every supported target.
  The ARM Linux targets are built on `manylinux_2_28` images because the older `manylinux2014`
  cross toolchain cannot compile the `ring` crate that rustls depends on.
* **release** runs only for tags and uploads all wheels and the sdist to PyPI.

`.github/workflows/doc.yml` builds this site with `mkdocs --strict` and deploys it to GitHub Pages.

## Cut a release

1. Bump `version` in `Cargo.toml`. The Python package version is read from there, so nothing else needs editing.
2. Commit, then tag and push:

```bash
git tag v0.4.0 && git push origin main v0.4.0
```

## Preview the docs locally

```bash
pip install mkdocs-material
mkdocs serve
```
