from flask.json import JSONEncoder
from bson import ObjectId

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, ObjectId):
                return str(obj)
            if isinstance(obj, bytes):
                return obj.decode("utf-8")
            if hasattr(obj, 'decode'):
                return obj.decode("utf-8")
            return JSONEncoder.default(self, obj)
        except TypeError:
            pass
        else:
            return JSONEncoder.default(self, obj)
        return JSONEncoder.default(self, obj)
