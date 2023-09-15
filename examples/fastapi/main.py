from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore

iot = IotCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    iot.background_loop_forever()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"Hello": "World"}


def mqtt_callback(data):
    print(f"iot >: {data}")


@app.get("/sub")
def sub():
    iot.subscribe("iot", mqtt_callback)
    return {"response": "subscribed"}


@app.get("/pub")
def pub():
    iot.publish("iot", "test")
    return {"response": "published"}

