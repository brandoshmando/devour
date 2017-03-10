try:
    import ujson as json
except ImportError:
    import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from devour.django import schemas, common
from devour.producers import GenericProducer
from devour import kafka


class ProducerModel(models.Model, GenericProducer):
    _produce = None
    _produce_extras = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._produce = kwargs.pop('produce', None)
        self._produce_extras = kwargs.pop('produce_extras', None)
        super(ProducerModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._produce = kwargs.pop('produce', None)
        self._produce_extras = kwargs.pop('produce_extras', None)
        super(ProducerModel, self).delete(*args, **kwargs)

    def produce(self, event=None, produce_extras=None, created=None, deleted=None):
        """
        master produce method. no need to override. use helper methods
        to tweak message data.
        """

        assert hasattr(self, 'ProducerConfig'), (
            'Model {0} requires ProducerConfig class to be declared.'.format(self.__class__.__name__)
        )

        # Prevent model from producing if
        # user manually passes in produce=False or
        # auto_produce is false
        if self._produce is False or\
           getattr(self.ProducerConfig, 'auto_produce', True) is False:
            # set back to None in case
            # two actions called b2b
            self._produce = None
            return False

        if not event:
            event = self._get_event(created, deleted)

        super(ProducerModel, self).produce(event, produce_extras)

    def get_message(self, event, topic, produce_extras=None):
        """
        avoid overriding this method. if custom tweaks to
        message are needed, do so with schema logic
        """
        source = self.get_source(event, topic)
        schema_class = self.get_schema(event, topic)

        assert schema_class is not None, (
            '{0} requires a schema_class to be declared on ProducerConfig class'.format(self.__class__.__name__)
        )

        message_data = schema_class(
            instance=self,
            context={'source': source, 'event': event},
            produce_extras=produce_extras
        ).data

        return message_data

    def _get_event(self, created, deleted):
        """
        returns CRUD event type. if you need a custom
        event, call .produce() manually and provide custom event
        instead of overriding this.
        """

        event = None
        if deleted:
            event = common.DELETE_EVENT
        elif created:
            event = common.CREATE_EVENT
        elif created is False and deleted is False:
            event = common.UPDATE_EVENT

        assert event is not None, (
            '{0} requires an event to be provided when calling .produce() manually'.format(self.__class__.__name__)
        )

        return event

    def _get_generic_topic(self):
        """
        attempts to create a generic topic if topic is not provided on
        ProducerConfig. based on app name and class name.
        """

        content_type = ContentType.objects.get_for_model(self.__class__)
        app_label = content_type.app_label

        return super(ProducerModel, self)._get_generic_topic(identifier=app_label)
