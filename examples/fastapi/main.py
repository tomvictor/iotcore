from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore, IotCoreBroker

iot = IotCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    IotCoreBroker("Broker").run_forever()
    iot.background_loop_forever()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


def mqtt_callback(data):
    print(f"iot >: {data}")


@app.get("/sub")
def read_root():
    iot.subscribe("iot", mqtt_callback)
    return {"response": "subscribed"}


@app.get("/pub")
def read_root():
    iot.publish("iot", "test")
    return {"response": "published"}


@app.get("/reconnect")
def read_root():
    iot.reconnect()
    return {"response": "ok"}
