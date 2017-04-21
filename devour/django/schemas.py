from django.apps import apps
from django.db import models
from devour.schemas import Schema

class ModelSchema(Schema):

    def __init__(self, data=None, instance=None, extras={}):
        assert data or instance, (
            '%s requires data or instance.' % self.__class__.__name__
        )

        self._data = data
        self._instance = instance
        self._model = self._instance.__class__
        self._extras = extras
        self._serialized_data = {}

    def serialize(self):
        if self._instance:
            serialized_data = {}
            attrs = self.get_attributes()
            for field_name in attrs:
                if hasattr(self._instance, field_name):
                    val = getattr(self._instance, field_name)
                    if hasattr(val, '__class__'):
                        if issubclass(val.__class__, models.Model):
                            try:
                                schema = getattr(self, key)
                                val = schema(val).data
                            except AttributeError:
                                # look for schema provided for
                                # attr. let pass and add full dict
                                # if none declared
                                pass

                    serialized_data[field_name] = val
        else:
            serialized_data = super(ModelSchema, self).serialize()

        return serialized_data

    def get_all(self):
        return [f.name for f in self._model._meta.get_fields()]
