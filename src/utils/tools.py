import json
from datetime import datetime
from uuid import uuid4



def load_config(path):
    with open(path, "r") as file:
        return json.load(file)


def generateUUID():
    return str(uuid4())


def convert_to_seconds(value, unit):
    if unit == 'min':
        return value * 60
    elif unit == 'h':
        return value * 3600
    return value

