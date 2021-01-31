from json import loads
from types import SimpleNamespace


def json_to_object(json_object):
    return loads(json_object, object_hook=lambda d: SimpleNamespace(**d))