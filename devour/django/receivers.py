from devour.django.models import ProducerModel

def produce_post_save(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
            instance.produce(created=created)

def produce_post_delete(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
            instance.produce(deleted=True)
