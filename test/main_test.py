import base64
import os.path
from pathlib import Path

import threading
import requests
import cv2


def get_project_root() -> Path:
    return Path(__file__).parent


class myThread(threading.Thread):
    def __init__(self, jpg_as_text):
        threading.Thread.__init__(self)
        self.jpg_as_text = jpg_as_text

    def run(self):
        response = requests.post("http://10.116.10.185/liveliness/getLiveness", json={'base64': str(self.jpg_as_text)})
        # response = requests.post("http://172.17.0.2:8000/getLiveness", json={'base64': self.jpg_as_text})
        print(response)


async def request(base):
    # response = requests.post("http://127.0.0.1:8000/getLiveness", json={'base64': jpg_as_text})
    response = requests.post("http://172.17.0.2:8000/getLiveness", json={'base64': base})
    print(response)


def test_get_liveness():
    img_path = os.path.join(get_project_root(), "test1.jpg")
    img = cv2.imread("test1.png")
    retval, buffer = cv2.imencode('.jpg', img)
    jpg_as_text = base64.b64encode(buffer)

    # Create new threads
    thread1 = myThread(jpg_as_text)
    thread2 = myThread(jpg_as_text)

    # Start new Threads
    thread1.start()
    # thread2.start()
    thread1.join()
    # thread2.join()
    # # response = requests.post("http://127.0.0.1:8000/getLiveness", json={'base64': jpg_as_text})
    # response = requests.post("http://172.17.0.2:8000/getLiveness", json={'base64': jpg_as_text})
    # print(response)
    return 0