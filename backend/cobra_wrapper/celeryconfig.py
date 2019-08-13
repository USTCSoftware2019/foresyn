broker_url = 'amqp://test:test123456@localhost:5672/test'
result_backend = 'django-db'
imports = ('cobra_wrapper.tasks',)
timezone = 'Asia/Shanghai'
task_annotations = {
    'tasks.cobra_fba': {
        'rate_limit': '10/s'
    },
    'tasks.cobra_fva': {
        'rate_limit': '10/s'
    }
}
