try:
    import ujson as json
except ImportError:
    import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from devour.django import schemas, common
from devour.producers import BaseProducer
from devour import kafka


class ProducerModel(models.Model, BaseProducer):
    _produce = False
    _produce_extras = {}
    _produce_context = {}

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._produce = kwargs.pop('produce', True)
        self._produce_context = kwargs.pop('produce_context', {})
        super(ProducerModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._produce = kwargs.pop('produce', True)
        self._produce_context = kwargs.pop('produce_context', {})
        super(ProducerModel, self).delete(*args, **kwargs)

    def get_schema(self, context):
        schema_class = super(ProducerModel, self).get_schema(context)
        return schema_class or schemas.ModelSchema

    def get_message(self, context, schema_class, extras):
        """
        avoid overriding this method. if custom tweaks to
        message are needed, do so with schema logic
        """

        message_data = schema_class(instance=self, extras=extras).data
        return message_data

    def _get_generic_topic(self):
        """
        creates a generic topic name if topic is not provided on
        ProducerConfig. based on app name and class name.
        """

        content_type = ContentType.objects.get_for_model(self.__class__)
        app_label = content_type.app_label

        return super(ProducerModel, self)._get_generic_topic(identifier=app_label)
