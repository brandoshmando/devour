from devour.django import schemas

class SimpleMessageSchema(schemas.ModelSchema):
    class Meta:
        attributes = ('message',)


class GenericSimpleMessageSchema(schemas.Schema):
    class Meta:
        attributes = ('message',)


class ProblemSchema(schemas.ModelSchema):
    class Meta:
        attributes = ('id', 'variables', 'solution_id')
