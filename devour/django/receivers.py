from devour.django.models import ProducerModel

def produce_post_save(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
            instance.produce(
                instance._produce_event, instance._produce_source,
                instance._produce_extras, instance._produce_context,
                created=created
            )

def produce_post_delete(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
            instance.produce(
                instance._produce_event, instance._produce_source,
                instance._produce_extras, instance._produce_context,
                deleted=True
            )
