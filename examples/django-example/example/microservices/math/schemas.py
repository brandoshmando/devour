from devour.schemas import Schema

class MathSchema(Schema):
    class Meta:
        attributes = ('id', 'variables', 'solution_id', 'event')
