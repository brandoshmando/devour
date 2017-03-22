from __future__ import unicode_literals

from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from devour.django.models import ProducerModel
from example.schemas import SimpleMessageSchema, ProblemSchema

class SimpleMessage(ProducerModel):
    message = models.TextField()

    class ProducerConfig:
        topic = 'test'
        schema_class = SimpleMessageSchema
        producer_type = 'sync_producer'

class Solution(models.Model):
    value = models.IntegerField()

class Problem(ProducerModel):
    variables = models.CharField(max_length=1024, validators=[validate_comma_separated_integer_list], default='0')
    solution = models.OneToOneField(Solution,
        null=True, blank=True,
        on_delete=models.CASCADE, related_name='problem'
    )

    class ProducerConfig:
        topic = 'math'
        producer_type = 'sync_producer'
        compression = 1
        schema_class = ProblemSchema
