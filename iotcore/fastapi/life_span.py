from fastapi import FastAPI
from contextlib import asynccontextmanager
from iotcore import IotCoreBroker


@asynccontextmanager
async def iotcore_broker(app: FastAPI):
    broker = IotCoreBroker(name="FastApiServer")
    broker.run_forever()
    yield
