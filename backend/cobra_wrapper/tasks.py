import json

from celery import shared_task

from . import models


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
def cobra_fba_save(pk, result, task_id):
    save_result(get_object_or_none(models.CobraFba, pk), result, task_id)


@shared_task
def cobra_rge_fba_save(pk, result, task_id):
    save_result(get_object_or_none(models.CobraRgeFba, pk), result, task_id)


@shared_task
def cobra_fva_save(pk, result, task_id):
    save_result(get_object_or_none(models.CobraFva, pk), result, task_id)
