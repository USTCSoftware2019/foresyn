from celery import Celery

app = Celery('cobra_computation')
app.config_from_object('cobra_computation.celeryconfig')
