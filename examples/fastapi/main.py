from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore


def mqtt_callback(data):
    print(f"iot >: {data}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    iot = IotCore()
    iot.start_broker()
    iot.background_loop_forever()
    iot.subscribe("iot", mqtt_callback)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}
