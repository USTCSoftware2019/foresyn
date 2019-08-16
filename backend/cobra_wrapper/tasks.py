from celery import shared_task

from .models import CobraFba, CobraFva


@shared_task
def cobra_fba_save(pk, result, task_id):
    try:
        instance = CobraFba.objects.get(pk=pk)
    except CobraFba.DoesNotExist:
        return

    if str(instance.task_id) != task_id:
        return

    instance.result = result
    instance.task_id = None
    instance.full_clean()
    instance.save()


@shared_task
def cobra_fva_save(pk, result, task_id):
    try:
        instance = CobraFva.objects.get(pk=pk)
    except CobraFba.DoesNotExist:
        return

    if str(instance.task_id) != task_id:
        return

    instance.result = result
    instance.task_id = None
    instance.full_clean()
    instance.save()
