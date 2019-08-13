broker_url = 'amqp://test:test123456@localhost:5672/test'
result_backend = 'rpc://'
imports = ('cobra_computation.tasks',)
timezone = 'Asia/Shanghai'
task_annotations = {
    'cobra_computation.tasks.cobra_fba': {
        'rate_limit': '10/s'
    },
    'cobra_computation.tasks.cobra_fva': {
        'rate_limit': '10/s'
    }
}
task_ignore_result = True
task_routes = ([
    ('cobra_computation.tasks.*', {'queue': 'feeds'}),
    ('cobra_wrapper.tasks.*', {'queue': 'results'}),
],)
