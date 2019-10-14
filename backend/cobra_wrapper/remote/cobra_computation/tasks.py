import json
from typing import List

import cobra.manipulation
from cobra.flux_analysis import flux_variability_analysis

from .celery import app
from .utils import load_sbml


# TODO(myl7): Better error solution
def check_cobra_model_component_available(cobra_model: cobra.Model, component_name: str, checked_list: List[str]):
    components = [component.id for component in getattr(cobra_model, component_name, ())]
    for value in checked_list:
        if value not in components:
            return {
                'errors': '{name} {value} is not in the cobra model'.format(name=component_name, value=value),
                'kwargs': {
                    'name': component_name,
                    'value': value,
                }
            }


@app.task
def cobra_fba(pk, model_sbml, deleted_genes):
    cobra_model = load_sbml(model_sbml)
    if len(deleted_genes) > 0:
        checking_result = check_cobra_model_component_available(cobra_model, 'genes', deleted_genes)
        if checking_result is None:
            app.send_task(
                'cobra_wrapper.tasks.cobra_fba_save',
                kwargs={
                    'pk': pk,
                    'result': json.dumps(checking_result),
                    'task_id': app.current_task.request.id,
                },
                queue='cobra_results',
                routing_key='cobra_result.fba',
            )
            return

        cobra.manipulation.delete_model_genes(cobra_model, deleted_genes, cumulative_deletions=True)
    result_object = cobra_model.optimize()
    result: dict = json.loads(result_object.to_frame().to_json())
    result['objective_value'] = result_object.objective_value
    result['status'] = result_object.status
    app.send_task(
        'cobra_wrapper.tasks.cobra_fba_save',
        kwargs={
            'pk': pk,
            'result': json.dumps(result),
            'task_id': app.current_task.request.id,
        },
        queue='cobra_results',
        routing_key='cobra_result.fba',
    )


@app.task
def cobra_fva(pk, model_sbml, reaction_list, loopless, fraction_of_optimum, pfba_factor, deleted_genes):
    cobra_model = load_sbml(model_sbml)
    checking_result = check_cobra_model_component_available(cobra_model, 'reactions', reaction_list)
    if checking_result is None:
        app.send_task(
            'cobra_wrapper.tasks.cobra_fva_save',
            kwargs={
                'pk': pk,
                'result': json.dumps(checking_result),
                'task_id': app.current_task.request.id,
            },
            queue='cobra_results',
            routing_key='cobra_result.fva',
        )
        return

    if len(deleted_genes) > 0:
        checking_result = check_cobra_model_component_available(cobra_model, 'genes', deleted_genes)
        if checking_result is None:
            app.send_task(
                'cobra_wrapper.tasks.cobra_fva_save',
                kwargs={
                    'pk': pk,
                    'result': json.dumps(checking_result),
                    'task_id': app.current_task.request.id,
                },
                queue='cobra_results',
                routing_key='cobra_result.fva',
            )
            return

        cobra.manipulation.delete_model_genes(cobra_model, deleted_genes, cumulative_deletions=True)
    result = flux_variability_analysis(
        cobra_model, reaction_list, loopless, fraction_of_optimum, pfba_factor).to_json()
    app.send_task(
        'cobra_wrapper.tasks.cobra_fva_save',
        kwargs={
            'pk': pk,
            'result': result,
            'task_id': app.current_task.request.id,
        },
        queue='cobra_results',
        routing_key='cobra_result.fva',
    )
