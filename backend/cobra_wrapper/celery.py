from celery import Celery

app = Celery()
app.config_from_object('cobra_wrapper.tasks')
