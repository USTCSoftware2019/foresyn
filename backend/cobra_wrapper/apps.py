from django.apps import AppConfig
from django.db.models.signals import pre_save, pre_delete


class CobraWrapperConfig(AppConfig):
    name = 'cobra_wrapper'

    def ready(self):
        from .signals.celery_feeds import call_cobra_fba, call_cobra_fva, revoke_cobra_fba, revoke_cobra_fva
        pre_save.connect(call_cobra_fba, sender='cobra_wrapper.CobraFba', dispatch_uid='call_cobra_fba')
        pre_save.connect(call_cobra_fva, sender='cobra_wrapper.CobraFva', dispatch_uid='call_cobra_fva')
        pre_delete.connect(revoke_cobra_fba, sender='cobra_wrapper.CobraFba', dispatch_uid='revoke_cobra_fba')
        pre_delete.connect(revoke_cobra_fva, sender='cobra_wrapper.CobraFva', dispatch_uid='revoke_cobra_fva')
