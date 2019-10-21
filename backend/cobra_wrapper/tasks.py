import json

from celery import shared_task

from . import models
from regulation.tasks import gene_regulation


def get_object_or_none(model_class, pk):
    try:
        return model_class.objects.get(pk=pk)
    except models.CobraFba.DoesNotExist:
        return None


def save_result(instance, result, task_id):
    if instance is None or str(instance.task_id) != task_id:
        return
    instance.result = result
    instance.ok = json.loads(result)['ok']
    instance.task_id = None
    instance.full_clean()
    instance.save()


@shared_task
def cobra_fba_save(pk, result, task_id, computation_type):
    if computation_type == 'normal':
        save_result(get_object_or_none(models.CobraFba, pk), result, task_id)
    elif computation_type == 'regular':
        instance = get_object_or_none(models.CobraRgeFba, pk)
        if instance is None:
            return
        gene_regulation.delay(**{
            'pk': pk,
            'task_id': task_id,
            'model_pk': instance.model.pk,
            'shadow_prices': {
                shadow_price['name']: shadow_price['value'] for shadow_price in json.loads(result)['shadow_prices']
            },
        })
    elif computation_type == 'regular_again':
        save_result(get_object_or_none(models.CobraRgeFba, pk), result, task_id)


@shared_task
def cobra_rge_fba_save(pk, result, task_id):
    save_result(get_object_or_none(models.CobraRgeFba, pk), result, task_id)


@shared_task
def cobra_fva_save(pk, result, task_id):
    save_result(get_object_or_none(models.CobraFva, pk), result, task_id)
