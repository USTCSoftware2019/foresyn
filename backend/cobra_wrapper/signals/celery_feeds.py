from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
import cobra
from celery.result import AsyncResult

from cobra_wrapper.models import CobraFba, CobraFva

from backend.celery import app


@receiver(pre_save, sender=CobraFba)
def call_cobra_fba(sender, **kwargs):
    instance = kwargs['instance']
    cobra_model = instance.model.build()
    result = app.send_task(
        'cobra_computation.tasks.cobra_fba',
        args=[cobra.io.to_json(cobra_model)],
        kwargs={},
        queue='cobra_feeds',
        routing_key='cobra_feed.fba'
    )
    instance.task_id = result.id


@receiver(pre_save, sender=CobraFva)
def call_cobra_fva(sender, **kwargs):
    instance = kwargs['instance']
    cobra_model = instance.model.build()
    cobra_fva_kwargs = {
        'reaction_list': (
            [reaction.cobra_id for reaction in instance.reaction_list.all()] if instance.reaction_list.all() else None
        ),
        'loopless': instance.loopless,
        'fraction_of_optimum': instance.fraction_of_optimum,
        'pfba_factor': instance.pfba_factor
    }
    result = app.send_task(
        'cobra_computation.tasks.cobra_fva',
        args=[cobra.io.to_json(cobra_model)],
        kwargs=cobra_fva_kwargs,
        routing_key='cobra_feed.fva'
    )
    instance.task_id = result.id


@receiver(pre_delete, sender=CobraFba)
def revoke_cobra_fba(sender, **kwargs):
    instance = kwargs['instance']
    if not instance.result:
        result = AsyncResult(instance.task_id, app=app)
        result.revoke(terminate=True)


@receiver(pre_delete, sender=CobraFva)
def revoke_cobra_fva(sender, **kwargs):
    instance = kwargs['instance']
    if not instance.result:
        result = AsyncResult(instance.task_id, app=app)
        result.revoke(terminate=True)
