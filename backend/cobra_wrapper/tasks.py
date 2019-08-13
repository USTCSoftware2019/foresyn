from .celery import app
from .models import CobraFba, CobraFva


@app.task
def cobra_fba_save(result, task_id):
    try:
        model_object = CobraFba.objects.get(task_id=task_id)
    except CobraFba.DoesNotExist:
        return
    model_object.result = result
    model_object.save()


@app.task
def cobra_fva_save(result, task_id):
    try:
        model_object = CobraFva.objects.get(task_id=task_id)
    except CobraFba.DoesNotExist:
        return
    model_object.result = result
    model_object.save()
