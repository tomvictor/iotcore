from fastapi import FastAPI
from iotcore.fastapi import iotcore_broker

app = FastAPI(lifespan=iotcore_broker)


@app.get("/")
def read_root():
    return {"Hello": "World"}
