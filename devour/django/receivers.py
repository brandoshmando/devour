from devour.django.models import ProducerModel

def produce_post_save(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
        if self._produce is False or\
           getattr(self.ProducerConfig, 'auto_produce', True) is False:
           # Prevent model from producing if
           # user manually passes in produce=False or
           # auto_produce is false
           return False

        #produce logic
        self._produce_context['event'] = self._get_event(created, deleted=False)
        instance.produce(instance._produce_context)

        # set back to empty in case
        # two actions called on same instance
        self._produce = False
        self._produce_context = {}

def produce_post_delete(sender, instance=None, created=False, **kwargs):
    if issubclass(instance.__class__, ProducerModel):
        if self._produce is False or\
           getattr(self.ProducerConfig, 'auto_produce', True) is False:
           # Prevent model from producing if
           # user manually passes in produce=False or
           # auto_produce is false
           return False

        #produce logic
        self._produce_context['event'] = self._get_event(created=False, deleted=True)
        instance.produce(instance._produce_context)

        # set back to empty in case
        # 2+ actions called on same instance
        self._produce = False
        self._produce_context = {}
