from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import start_mqtt_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mqtt_server()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}
