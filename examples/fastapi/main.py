"""FastAPI app with an embedded MQTT broker and client.

    uvicorn examples.fastapi.main:app

Then connect any MQTT client to localhost:1883, or use the HTTP endpoints below.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from iotcore import IotCore

iot = IotCore()  # starts the broker on localhost:1883 unless one is already running


@asynccontextmanager
async def lifespan(app: FastAPI):
    iot.start()  # called inside the event loop, so async callbacks work
    yield
    iot.stop()


app = FastAPI(lifespan=lifespan)
latest = {}


@iot.accept("sensors/#")
async def on_sensor(topic: str, data: str):
    latest[topic] = data


@app.get("/")
def home():
    return {"latest": latest}


@app.get("/pub")
def pub(topic: str = "sensors/temperature", data: str = "21.5"):
    iot.publish(topic, data)
    return {"published": topic}


@app.get("/unsub")
def unsub():
    iot.unsubscribe("sensors/#")
    return {"unsubscribed": "sensors/#"}
