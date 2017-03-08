try:
    import ujson as json
except ImportError:
    import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from devour.django import schemas, common, kafka


class ProducerModel(models.Model):
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

    def produce(self, event=None, created=None, deleted=None, produce_extras=None):
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
        topic = self.get_topic(event)

        source = self.get_source(event, topic)
        schema_class = self.get_schema(event, topic)
        partition_key = self.get_partition_key(event, topic)

        message = schema_class(
            instance=self,
            context={'topic': topic, 'event': event, 'source': source},
            extra_data=produce_extras
        ).data

        p = kafka.get_producer(topic, self.ProducerConfig.producer_type)
        p.produce(message, partition_key)

    def get_topic(self, event):
        """
        override this with custom logic
        to return desired topic name (str)
        based on event. should never return None
        """

        return getattr(self.ProducerConfig, 'topic', self._get_generic_topic())

    def get_source(self, event, topic):
        return self.__class__.__name__

    def get_schema(self, event, topic):
        """
        override this with custom logic
        to return desired schema class
        based on event or topic. should never return None
        """

        schema_class = getattr(self.ProducerConfig, 'schema_class', None)

        assert schema_class is not None, (
            '{0} requires a schema_class to be declared on ProducerConfig class'.format(self.__class__.__name__)
        )

        return schema_class

    def get_partition_key(self, event, topic):
        """
        attempts to get partition key from your model based on topic name. avoid
        overriding this. complex partitioning logic should be done
        on initial save of your model as you don't want such
        logic to be called with each produce event.
        """

        key = None
        if hasattr(self, topic +'_partition_key'):
            key = getattr(self, attr)
        elif hasattr(self, 'partition_key'):
            key = getattr(self, 'partition_key')

        return key

    def _get_event(self, created, deleted):
        """
        returns CRUD event type. if you need a custom
        event, call .produce() manually and provide custom event
        instead of overriding this.
        """

        event = None
        if deleted:
            event = choices.DELETE_EVENT
        elif created:
            event = choices.CREATE_EVENT
        elif created is False and deleted is False:
            event = choices.UPDATE_EVENT

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

        return '{0}__{1}'.format(app_label, self.__class__.__name__)
