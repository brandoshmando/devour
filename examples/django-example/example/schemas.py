from devour.django import schemas

class SimpleMessageSchema(schemas.ModelSchema):
    class Meta:
        model = 'example.SimpleMessage'
        attributes = ('message',)
