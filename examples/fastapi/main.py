from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore


def mqtt_callback(topic, data):
    print(f"Python> {topic}: {data}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    core = IotCore("", 1883, mqtt_callback)
    core.initialize_broker()
    core.begin_subscription()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}
