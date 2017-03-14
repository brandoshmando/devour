from __future__ import unicode_literals

import os
from django.apps import AppConfig
from django.db.models import signals


class DevourConfig(AppConfig):
    name = 'devour.django'
    verbose_name = 'devour app config'

    def ready(self):
        from django.db.models.signals import post_save, post_delete
        from devour.django.receivers import produce_post_save, produce_post_delete
        from django.conf import settings
        import os

        signal_types = {
            'post_save': produce_post_save,
            'post_delete': produce_post_delete
        }

        if getattr(settings, 'KAFKA_CONFIG', None):
            try:
                excl = settings.KAFKA_CONFIG['producers'].get('exclude')
            except:
                #TODO: Error handling
                excl = []
                pass

            for s,f in signal_types.items():
                if next((True for ex in excl if s == ex), False):
                    del signal_types[s]

            for sig in signal_types.keys():
                getattr(signals, sig).connect(signal_types[sig])
