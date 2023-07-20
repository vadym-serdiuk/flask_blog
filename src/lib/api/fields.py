from flask import url_for
from flask_restful.fields import Raw, MarshallingException


class DetailApiUrl(Raw):
    def __init__(self, resource, path_attr, obj_attr, **kwargs):
        super(DetailApiUrl, self).__init__(**kwargs)
        self.resource = resource
        self.path_attr = path_attr
        self.obj_attr = obj_attr

    def output(self, key, obj):
        try:
            url = url_for(self.resource, **{self.path_attr: getattr(obj, self.obj_attr, '')})
        except TypeError as te:
            raise MarshallingException(te)
        else:
            return url
