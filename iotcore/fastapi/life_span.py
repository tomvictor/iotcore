from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCore

@asynccontextmanager
async def iotcore_broker(app: FastAPI):
    iot = IotCore()
    iot.start_broker()
    yield
