class Schema(object):
    def __init__(self, data, extras={}):
        self._data = data
        self._extras = extras
        self._serialized_data = {}

    @property
    def data(self):
        # immutable after the first call
        if not self._serialized_data:
            self._serialized_data = self.serialize()
            if self._extras:
                self._serialized_data.update(self._extras)
        return self._serialized_data

    def serialize(self):
        serialized_data = {}
        if self._data:
            attrs = self.get_attributes()
            for key in attrs:
                try:
                    val = self._data[key]
                except KeyError:
                    # don't add attributes that
                    # don't exist in dict already
                    continue

                if isinstance(val, dict):
                    try:
                        schema = getattr(self, key)
                        val = schema(val).data
                    except AttributeError:
                        # look for schema provided for
                        # attr. let pass and add full dict
                        # if none declared
                        pass

                serialized_data[key] = val
        return serialized_data

    def get_all(self):
        return self._data.keys()

    def get_attributes(self):
        attributes = None
        if hasattr(self, 'Meta'):
            attributes = getattr(self.Meta, 'attributes', None)
        return attributes or self.get_all()
