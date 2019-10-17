import json

from celery import shared_task

from .models import CobraFba, CobraFva


def get_object_or_none(model_class, pk):
    try:
        return model_class.objects.get(pk=pk)
    except CobraFba.DoesNotExist:
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
    save_result(get_object_or_none(CobraFba, pk), result, task_id)


@shared_task
def cobra_fva_save(pk, result, task_id):
    save_result(get_object_or_none(CobraFva, pk), result, task_id)
