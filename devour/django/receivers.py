from devour.django.utils.helpers import _get_event
from devour.django.models import ProducerModel


def produce_post_save(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
        if instance._produce is False or\
           getattr(instance.ProducerConfig, 'auto_produce', True) is False:
           # Prevent model from producing if
           # user manually passes in produce=False or
           # auto_produce is false
           return False

        #produce logic
        event = _get_event(created=created)
        instance._produce_extras['event'] = event
        instance._produce_context['event'] = event
        instance.produce(
            instance._produce_context,
            instance._produce_extras
        )

        # set back to empty in case
        # two actions called on same instance
        instance._produce = False
        instance._produce_context = {}

def produce_post_delete(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
        if instance._produce is False or\
           getattr(instance.ProducerConfig, 'auto_produce', True) is False:
           # Prevent model from producing if
           # user manually passes in produce=False or
           # auto_produce is false
           return False

        #produce logic
        event = _get_event(created=False, deleted=True)
        instance._produce_extras['event'] = event
        instance._produce_context['event'] = event
        instance.produce(
            instance._produce_context,
            instance._produce_extras
        )

        # set back to empty in case
        # 2+ actions called on same instance
        instance._produce = False
        instance._produce_context = {}
