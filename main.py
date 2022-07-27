import time
from typing import Optional
import json

from fastapi import FastAPI
from pydantic import BaseModel
import redis3, uuid

CHANNEL = "spoof_request_queue"
redis_address = "192.168.0.106"
redis: redis3.Redis
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global redis
    redis = redis3.Redis(host=redis_address, port=31500)


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
