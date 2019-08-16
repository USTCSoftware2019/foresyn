from django.db.models.signals import pre_delete
from django.dispatch import receiver
from celery.result import AsyncResult

from cobra_wrapper.models import CobraFba, CobraFva

from backend.celery import app


@receiver(pre_delete, sender=CobraFba)
def revoke_cobra_fba(sender, **kwargs):
    instance = kwargs['instance']
    if instance.task_id:
        result = AsyncResult(instance.task_id, app=app)
        result.revoke()


@receiver(pre_delete, sender=CobraFva)
def revoke_cobra_fva(sender, **kwargs):
    instance = kwargs['instance']
    if instance.task_id:
        result = AsyncResult(instance.task_id, app=app)
        result.revoke()
