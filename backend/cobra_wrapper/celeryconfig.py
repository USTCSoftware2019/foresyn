BROKER_URL = 'amqp://test:test123456@localhost:5672/test'
RESULT_BACKEND = 'rpc://'
IMPORTS = ('cobra_wrapper.tasks',)
TIMEZONE = 'Asia/Shanghai'
TASK_ANNOTATIONS = {
    'cobra_computation.tasks.cobra_fba': {
        'rate_limit': '10/s'
    },
    'cobra_computation.tasks.cobra_fva': {
        'rate_limit': '10/s'
    }
}
