from json import loads
from types import SimpleNamespace


def deserialize_json(json_object):
    return loads(json_object, object_hook=lambda d: SimpleNamespace(**d))