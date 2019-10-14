import json

import cobra.manipulation
from cobra.flux_analysis import flux_variability_analysis

from .celery import app
from .utils import load_sbml


@app.task
def cobra_fba(pk, model_sbml, deleted_genes):
    cobra_model = load_sbml(model_sbml)
    if len(deleted_genes) > 0:
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
    if len(deleted_genes) > 0:
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
