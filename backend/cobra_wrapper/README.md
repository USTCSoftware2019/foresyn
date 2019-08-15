# cobra_wrapper

Django app to manage COBRApy models, reactions and metabolites and preform computation like FBA and FVA basing on them

## Environment

GNU/Linux x86_64

## Prerequisites

* [RabbitMQ][rabbitmq] >=3.7.15

## Setup

Create a user and vhost of RabbitMQ to provide the app with a broker

```bash
sudo rabbitmqctl add_user myuser mypassword
sudo rabbitmqctl add_vhost myvhost
sudo rabbitmqctl set_user_tags myuser mytag
sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
sudo systemctl restart rabbitmq
``` 

Don't forget to change `myuser`, `mypassword`, `myvhost` to respective names

## Usage

Start two workers first

```bash
cd ./remote
celery worker -l info -A cobra_computation -Q cobra_feeds
```

```bash
cd ..
celery worker -l info -A backend -Q cobra_results
```

Then start Django to use the app

[rabbitmq]: https://www.rabbitmq.com/
