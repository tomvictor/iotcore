from typing import Union
import iotcore

from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def callback(payload):
    print(f"Received payload in python: {payload}")


def write_notification(email: str, message=""):
    core = iotcore.IotCore(callback)
    core.log("msg from python")
    core.publish("tom/iot", "hello")
    core.subscribe("test")
    core.run()


@app.get("/test/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
