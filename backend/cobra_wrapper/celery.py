from celery import Celery

app = Celery(backend='rpc://', broker='')
app.config_from_object('cobra_wrapper.celeryconfig')
