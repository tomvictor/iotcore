from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore

iot_core = IotCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    iot_core.run()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}
