class Schema(object):
    def __init__(self, data, *args, **kwargs):
        self._init_data = data or {}
        self._serialized_data = None

        assert hasattr(self, 'Meta'), (
            '{0} requires a Meta class to be declared'.format(self.__class__.__name__)
        )

    @property
    def data(self):
        if not hasattr(self.Meta, 'attributes'):
            return self._init_data

        if not self._serialized_data:
            self._serialized_data = {}
            for key in self.Meta.attributes:
                val = self._init_data.get(key)
                if type(val) == dict:
                    try:
                        schema = getattr(self, key)
                        val = schema(val).data
                    except AttributeError:
                        # look for schema provided for
                        # attr. let pass and add full dict
                        # if none declared
                        pass

                self._serialized_data[key] = val

        return self._serialized_data
