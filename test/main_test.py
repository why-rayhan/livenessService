import base64
import os.path

import requests
import cv2

from main import get_project_root


def test_get_liveness():
    img_path = os.path.join(get_project_root(), "test1.jpg")
    img = cv2.imread("test1.png")
    retval, buffer = cv2.imencode('.jpg', img)
    jpg_as_text = base64.b64encode(buffer)
    response = requests.post("http://127.0.0.1:8000/getLiveness", json={'base64': jpg_as_text})
    print(response)
