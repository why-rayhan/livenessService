import json
import time

import redis3
import tensorflow as tf
import cv2
import numpy as np
import base64
import os
from pathlib import Path
import random

from dotenv import load_dotenv

redis: redis3.Redis = None
threshold = .6
CHANNEL = ""
model: tf.keras.Model = None
reconstructed_model: tf.keras.Model


def get_project_root() -> Path:
    return Path(__file__).parent


def init():
    global redis, CHANNEL
    load_dotenv()
    env = os.environ
    CHANNEL = env.get("QUEUE_CHANNEL")
    redis_address = env.get("REDIS_ADDRESS")
    redis_port = env.get("REDIS_PORT")
    redis = redis3.Redis(host=redis_address, port=int(redis_port))

    global model, reconstructed_model
    version = cv2.version
    model_directory = os.path.join(get_project_root(), "model", "weight", "patch")
    ab_model_directory = os.path.join(get_project_root(), "model", "weight", "model_refined")
    print(version.opencv_version)
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
    config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

    model = tf.keras.models.load_model(model_directory)
    reconstructed_model = tf.keras.models.load_model(ab_model_directory)


MAX_PATCH_PER_FACE = 20
PATCH_WIDTH = 96
PATCH_HEIGHT = 96


def base64_to_img(uri):
    # encoded_data = uri.split(',')[1]
    im_bytes = base64.b64decode(uri)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    # nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def get_patches(face, w, h):
    patches = []
    if face is not None and w > 100 and h > 100:

        total_patches = min(int(w / PATCH_WIDTH) * 2, int(h / PATCH_HEIGHT) * 2, MAX_PATCH_PER_FACE)

        for i in range(total_patches):
            x = random.randint(0, w - PATCH_WIDTH - 1)
            y = random.randint(0, h - PATCH_HEIGHT - 1)
            patch = face[y:y + PATCH_HEIGHT, x:x + PATCH_WIDTH]
            patches.append(patch)
    return patches


def predict_from_ab_model(frame):
    frame = cv2.resize(frame, (224, 224))
    np_image = np.asarray(frame).astype('float32') / 255
    # np_image = transform.resize(np_image, (224, 224, 3))
    np_image = np.expand_dims(np_image, axis=0)
    prediction = reconstructed_model.predict(np_image)

    if prediction[0][0] > 0.5:
        return 'fake'
    return 'real'


def predict_from_patch_model(frame):
    h, w, _ = frame.shape
    patches = get_patches(frame, w, h)
    total_patches = len(patches)
    patches = np.reshape(patches, [total_patches, PATCH_HEIGHT, PATCH_WIDTH, 3])
    patches = patches / 255
    result = model.predict_on_batch(patches)
    print(result)
    result = np.argmax(result, axis=-1)
    verdict_real = np.sum(result)
    verdict = "fake"
    if verdict_real / total_patches > threshold:
        verdict = "real"
    return verdict


if __name__ == "__main__":

    init()
    print("initialized")

    while True:
        try:
            time.sleep(.1)

            item = redis.lpop(CHANNEL)
            if item is None:
                continue
            print("frame found")

            item_dict = json.loads(item)
            frame = item_dict['frame']
            id = item_dict['id']

            try :
                img = base64_to_img(frame)

                verdict = predict_from_patch_model(img)
                verdict2 = predict_from_ab_model(img)

                log = "verdict: " + verdict + "  verdict2: " + verdict2
                if verdict == "fake":
                    verdict = verdict2

                result = json.dumps({"verdict": verdict, "log": log})
                redis.publish(id, result)
                print("frame published")
            except Exception as e:
                print(e)
                result = json.dumps({"verdict": "error", "log": e})
                redis.publish(id, result)
        except Exception as e:
            print(e)