# import json
import pickle


class Serializer:

    def serialize(self, data):
        # TODO: Fix case when
        # TODO: multiple dicts are incoming
        # return json.dumps(data).encode()

        return pickle.dumps(data)

    def deserialize(self, data):
        # TODO: Fix case when
        # TODO: multiple dicts are incoming
        # return json.loads(data)

        return pickle.loads(data)
