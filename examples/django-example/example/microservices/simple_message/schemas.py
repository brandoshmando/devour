from devour import schemas

class SimpleMessageConsumerSchema(schemas.Schema):
    class Meta:
        attributes = ('message',)
