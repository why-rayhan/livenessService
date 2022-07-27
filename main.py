import os
import time
from typing import Optional
import json

from fastapi import FastAPI
from pydantic import BaseModel
import redis3, uuid

CHANNEL = os.environ.get("QUEUE_CHANNEL")
redis_address = os.environ.get("REDIS_ADDRESS")
redis_port = os.environ.get("REDIS_PORT")
redis: redis3.Redis
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global redis
    redis = redis3.Redis(host=redis_address, port=int(redis_port))


class Item(BaseModel):
    base64: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/getLiveness")
def get_liveness(item: Item):

    id = str(uuid.uuid4())
    # print(id)
    payload = {"id": id, "frame": item.base64}
    s = json.dumps(payload)
    redis.rpush(CHANNEL, s)
    p = redis.pubsub()

    p.subscribe(id)

    message = None
    print(time.time())
    for i in range(1200):
        message = p.get_message(ignore_subscribe_messages=True)
        if message is not None:
            break
        time.sleep(.1)

    return {"verdict": message['data']}
