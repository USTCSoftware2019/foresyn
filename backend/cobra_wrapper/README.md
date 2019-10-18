# cobra_wrapper

Django app to manage COBRApy models, reactions and metabolites and preform computation like FBA and FVA basing on them

## Environment

GNU/Linux x86_64

## Prerequisites

* [RabbitMQ][rabbitmq] >=3.7.15

## Setup

Broker settings in `settings.py` is RabbitMQ default user, password and vhost. To make a test, no more setup is required except installation of RabbitMQ

If required, create a user and vhost of RabbitMQ to provide the app with a broker

```bash
sudo rabbitmqctl add_user myuser mypassword
sudo rabbitmqctl add_vhost myvhost
sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
sudo systemctl restart rabbitmq
``` 

In the situation, the broker url should be `amqp://myuser:mypassword@localhost/myvhost`

Don't forget to change `myuser`, `mypassword`, `myvhost` to respective names

Move the broker to another host is OK, just change `localhost` in the broker url to respective host IP

## Usage

Start two workers first

```bash
cd ./remote
env PYTHONOPTIMIZE=1 celery worker -l info -A cobra_computation -Q cobra_feeds
```

```bash
cd ..
env PYTHONOPTIMIZE=1 celery worker -l info -A backend -Q cobra_results
```

Then start Django to use the app

[rabbitmq]: https://www.rabbitmq.com/
