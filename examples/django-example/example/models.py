from __future__ import unicode_literals

from django.db import models
from devour.django.models import ProducerModel
from example.schemas import SimpleMessageSchema

class SimpleMessage(ProducerModel):
    message = models.TextField()

    class ProducerConfig:
        topic = 'test'
        schema_class = SimpleMessageSchema
        producer_type = 'sync_producer'
