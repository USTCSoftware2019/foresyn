import json

from .models import Regulation
from django.core.exceptions import ObjectDoesNotExist
from bigg_database.models import Gene, Model
from cobra_wrapper.utils import load_sbml, dump_sbml
from celery import shared_task
from backend.celery import app
from cobra_wrapper.models import CobraModel
from tt import BooleanExpression


@shared_task
def gene_regulation(pk, task_id, model_pk, shadow_prices):
    cobra_model = CobraModel.objects.get(pk=model_pk).build()
    for gene in cobra_model.genes:
        gene_name = __get_gene_name(gene.id, cobra_model.id)
        try:
            regulation = Regulation.objects.get(gene=gene_name)
        except ObjectDoesNotExist:
            continue
        if not __check(regulation, cobra_model, shadow_prices):
            gene.knock_out()
    app.send_task(
        'cobra_computation.tasks.cobra_fba',
        kwargs={
            'pk': pk,
            'model_sbml': dump_sbml(cobra_model),
            'deleted_genes': [],
            'computation_type': 'regular_again',
            'task_id': task_id,
        },
        queue='cobra_feeds',
        routing_key='cobra_feed.fba',
    )


def __check(regulation, cobra_model, shadow_price):
    try:
        exp = BooleanExpression(regulation.rule)
    except Exception:
        return True
    tokens = exp.symbols
    value = []
    for i in tokens:
        if i.find('less_than') != -1:
            try:
                SP = shadow_price[i[0:i.find('less_than')] + '_c']
            except KeyError:
                value.append(False)
                continue
            if SP < 0:
                value.append(True)
            else:
                value.append(False)
        elif i.find('more_than') != -1:
            try:
                SP = shadow_price[i[0:i.find('more_than')] + '_c']
            except KeyError:
                value.append(False)
                continue
            if SP > 0:
                value.append(True)
            else:
                value.append(False)
        else:

            if __check_gene(cobra_model, i):
                value.append(True)
            else:
                value.append(False)
    truth = exp.evaluate(**dict(zip(tokens, value)))
    return truth


def __check_gene(cobra_model, gene_name):
    gene_id = __get_gene_id(gene_name, cobra_model.id)
    try:
        cobra_model.genes.get_by_id(gene_id)
    except KeyError:
        return False
    return True


def __get_gene_id(gene_name, model_name):
    try:
        model = Model.objects.get(bigg_id=model_name)
    except ObjectDoesNotExist:
        # print("no id in model")
        return None
    try:
        gene_id = model.gene_set.get(name=gene_name).bigg_id
    except ObjectDoesNotExist:
        return None
    return gene_id


def __get_gene_name(gene_id, model_name):
    try:
        model = Model.objects.get(bigg_id=model_name)
    except ObjectDoesNotExist:
        return None
    try:
        gene_name = model.gene_set.get(bigg_id=gene_id).name
    except ObjectDoesNotExist:
        return None
    return gene_name
