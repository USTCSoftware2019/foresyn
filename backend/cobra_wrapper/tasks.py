from celery import shared_task

from .models import CobraFba, CobraFva


def get_object_or_none(model_class, pk):
    try:
        return model_class.objects.get(pk=pk)
    except CobraFba.DoesNotExist:
        return None


@shared_task
def cobra_fba_save(pk, result, task_id):
    instance = get_object_or_none(CobraFba, pk)
    if instance is None or str(instance.task_id) != task_id:
        return

    instance.result = result
    instance.task_id = None
    instance.full_clean()
    instance.save()


@shared_task
def cobra_fva_save(pk, result, task_id):
    instance = get_object_or_none(CobraFva, pk)
    if instance is None or str(instance.task_id) != task_id:
        return

    instance.result = result
    instance.task_id = None
    instance.full_clean()
    instance.save()
