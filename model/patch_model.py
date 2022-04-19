from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import os

PROJECT_ROOT_DIR = os.path.dirname(find_dotenv())

from tensorflow import keras


# import os, inspect


def get_uncompiled_model(output_size: int):

    feature = keras.Sequential()
    feature.add(keras.layers.Conv2D(50, 5, input_shape=(96,96,3)))
    feature.add(keras.layers.BatchNormalization())
    feature.add(keras.layers.ReLU())
    feature.add(keras.layers.MaxPool2D(strides=2))

    feature.add(keras.layers.Conv2D(100, 3))
    feature.add(keras.layers.BatchNormalization())
    feature.add(keras.layers.ReLU())
    feature.add(keras.layers.MaxPool2D(strides=2))

    feature.add(keras.layers.Conv2D(150, 3))
    feature.add(keras.layers.BatchNormalization())
    feature.add(keras.layers.ReLU())
    feature.add(keras.layers.MaxPool2D(strides=2))

    feature.add(keras.layers.Conv2D(200, 3))
    feature.add(keras.layers.BatchNormalization())
    feature.add(keras.layers.ReLU())
    feature.add(keras.layers.MaxPool2D(strides=2))

    feature.add(keras.layers.Conv2D(250, 3))
    feature.add(keras.layers.BatchNormalization())
    feature.add(keras.layers.ReLU())
    feature.add(keras.layers.MaxPool2D(strides=2))

    output = keras.Sequential()

    output.add(keras.layers.Dense(1000))
    output.add(keras.layers.BatchNormalization())
    output.add(keras.layers.ReLU())
    output.add(keras.layers.Dropout(0.5))

    output.add(keras.layers.Dense(400))
    output.add(keras.layers.BatchNormalization())
    output.add(keras.layers.ReLU())
    output.add(keras.layers.Dense(output_size, activation="softmax"))

    model = keras.Sequential()
    model.add(feature)
    model.add(keras.layers.Flatten())
    model.add(output)
    return model


def get_compiled_model(output_size: int):
    model = get_uncompiled_model(output_size)
    model.compile(optimizer=keras.optimizers.RMSprop(learning_rate=1e-3),
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy', 'categorical_accuracy'])
    return model


cwd = os.path.abspath(os.path.dirname(__file__))
print(cwd)
