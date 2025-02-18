import json


class JSONSerializer:
    """ Serialisiert die Sitzungsdaten in JSON statt Pickle. """
    @staticmethod
    def dumps(obj):
        return json.dumps(obj)

    @staticmethod
    def loads(data):
        return json.loads(data)