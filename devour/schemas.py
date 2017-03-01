
class SchemaMeta(object):
    pass

class Schema(object):
    def __init__(self, data, *args, **kwargs):
        self._init_data = data
        self._serialized_data = None
        self._meta = self.Meta

    @property
    def data(self):
        if not self._serialized_data:
            self._serialized_data = {}
            for key in self._meta.attributes:
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
