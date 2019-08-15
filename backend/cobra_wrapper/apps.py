from django.apps import AppConfig
from django.db.models.signals import pre_delete


class CobraWrapperConfig(AppConfig):
    name = 'cobra_wrapper'

    def ready(self):
        from .signals.revoke_cobra_feeds import revoke_cobra_fba, revoke_cobra_fva
        pre_delete.connect(revoke_cobra_fba, sender='cobra_wrapper.CobraFba', dispatch_uid='revoke_cobra_fba')
        pre_delete.connect(revoke_cobra_fva, sender='cobra_wrapper.CobraFva', dispatch_uid='revoke_cobra_fva')
