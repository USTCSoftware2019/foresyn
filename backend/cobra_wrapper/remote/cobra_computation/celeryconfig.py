from kombu import Queue

broker_url = 'amqp://test:test123456@localhost:5672/test'
result_backend = 'rpc://'
imports = ('cobra_computation.tasks',)
timezone = 'Asia/Shanghai'
task_routes = {
    'cobra_computation.tasks.cobra_fba': {
        'queue': 'cobra_feeds',
        'routing_key': 'cobra_feed.fba',
    },
    'cobra_computation.tasks.cobra_fva': {
        'queue': 'cobra_feeds',
        'routing_key': 'cobra_feed.fva',
    },
    'cobra_wrapper.tasks.cobra_fba_save': {
        'queue': 'cobra_results',
        'routing_key': 'cobra_result.fba',
    },
    'cobra_wrapper.tasks.cobra_fva_save': {
        'queue': 'cobra_results',
        'routing_key': 'cobra_result.fva',
    },
}
task_queues = (
    Queue('default', routing_key='task.#'),
    Queue('cobra_feeds', routing_key='cobra_feed.#'),
    Queue('cobra_results', routing_key='cobra_result.#'),
)
task_default_exchange = 'tasks'
task_default_exchange_type = 'topic'
task_default_routing_key = 'task.default'
task_ignore_result = True
# task_annotations = {
#     'cobra_computation.tasks.cobra_fba': {
#         'rate_limit': '10/s'
#     },
#     'cobra_computation.tasks.cobra_fva': {
#         'rate_limit': '10/s'
#     }
# }
