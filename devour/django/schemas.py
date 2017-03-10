import inspect
from devour.schemas import Schema
from django.apps import apps

class ModelSchema(Schema):

    def __init__(self, data={}, instance=None, extra_data=None, context={}, *args, **kwargs):
        assert (data or instance), (
            '{0}.__init__() requires either data or instance as args'.format(self.__class__.__name__)
        )

        self._instance = instance
        self._extra_data = extra_data
        self._context = context
        super(ModelSchema, self).__init__(data, *args, **kwargs)

        if not getattr(self.Meta, 'model', None):
            setattr(self.Meta, 'model', apps.get_model(self.Meta.model))

    @property
    def data(self):
        source = self._context['source']
        event = self._context['event']

        if not self._serialized_data:
            if not self._instance:
                super(ModelSchema, self).data
                delf._serialized_data['source'] = source
                self._serialized_data['event'] = event
            else:
                #convert to python dictionary
                self._serialized_data = {
                    'source': source,
                    'event': event
                }

                for field_name in self.Meta.attributes:
                    if hasattr(self._instance, field_name):
                        val = getattr(self._instance, field_name)
                        if inspect.isclass(val):
                            # TODO: Logic that determines class type and value that should be gleaned
                            pass
                        self._serialized_data[field_name] = val

                if self._init_data:
                    for key,val in self._init_data.items():
                        if key in self.Meta.attributes:
                            if inspect.isclass(val):
                                # TODO: Raise exception that object is not json serailizable
                                pass
                            self._serialized_data[key] = val

            if self._extra_data:
                self._serialized_data['extra_data'] = self._extra_data

        return self._serialized_data
