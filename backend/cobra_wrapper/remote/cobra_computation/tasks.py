import json
from typing import List, Dict, Any, Optional

import cobra.manipulation
import cobra.exceptions
from cobra.flux_analysis import flux_variability_analysis

from .celery import app
from .utils import load_sbml


def get_result_kwargs(computation_type: str, pk: int, dict_result: Optional[Dict[str, Any]] = None,
                      is_error: bool = False) -> Dict[str, Any]:
    dict_result['ok'] = True if not is_error else False
    return {
        'name': 'cobra_wrapper.tasks.cobra_{}_save'.format(computation_type),
        'kwargs': {
            'pk': pk,
            'result': json.dumps(dict_result),
            'task_id': app.current_task.request.id,
        },
        'queue': 'cobra_results',
        'routing_key': 'cobra_result.{}'.format(computation_type),
    }


def check_cobra_model_component_available(cobra_model: cobra.Model, component_name: str,
                                          checked_list: List[str]) -> Optional[Dict[str, Any]]:
    allowed_list = [component.id for component in getattr(cobra_model, component_name, ())]
    for value in checked_list:
        if value not in allowed_list:
            return {
                'error': '{component_name} {value} is not in the cobra model'.format(
                    component_name=component_name, value=value),
                'kwargs': {
                    'name': component_name,
                    'value': value,
                }
            }


def report_cobra_computation_error(error: Exception) -> Dict[str, Any]:
    if isinstance(error, (cobra.exceptions.OptimizationError, cobra.exceptions.SolverNotFound)):
        error_name = error.__name__
    else:
        error_name = 'UnknownException'
    return {
        'error': 'In computation a {error_name} is raised'.format(error_name=error_name),
        'kwargs': {
            'error_name': error_name,
        },
    }


@app.task
def cobra_fba(pk, model_sbml, deleted_genes):
    cobra_model = load_sbml(model_sbml)
    if len(deleted_genes) > 0:
        checking_result = check_cobra_model_component_available(cobra_model, 'genes', deleted_genes)
        if checking_result is not None:
            app.send_task(**get_result_kwargs('fba', pk, checking_result, is_error=True))
            return
        cobra.manipulation.delete_model_genes(cobra_model, deleted_genes, cumulative_deletions=True)
    try:
        result_object = cobra_model.optimize()
    except Exception as error:
        error_result = report_cobra_computation_error(error)
        app.send_task(**get_result_kwargs('fba', pk, error_result, is_error=True))
        return
    result = {
        'objective_value': result_object.objective_value, 'status': result_object.status,
        'fluxes': [{'name': name, 'value': value} for name, value in result_object.fluxes.to_dict().items()],
        'reduced_costs': [{'name': name, 'value': value}
                          for name, value in result_object.reduced_costs.to_dict().items()],
        'shadow_prices': [{'name': name, 'value': value}
                          for name, value in result_object.shadow_prices.to_dict().items()],
    }
    app.send_task(**get_result_kwargs('fba', pk, result))


@app.task
def cobra_fva(pk, model_sbml, reaction_list, loopless, fraction_of_optimum, pfba_factor, deleted_genes):
    cobra_model = load_sbml(model_sbml)
    checking_result = check_cobra_model_component_available(cobra_model, 'reactions', reaction_list)
    if checking_result is not None:
        app.send_task(**get_result_kwargs('fva', pk, checking_result, is_error=True))
        return
    if len(deleted_genes) > 0:
        checking_result = check_cobra_model_component_available(cobra_model, 'genes', deleted_genes)
        if checking_result is not None:
            app.send_task(**get_result_kwargs('fva', pk, checking_result, is_error=True))
            return
        cobra.manipulation.delete_model_genes(cobra_model, deleted_genes, cumulative_deletions=True)
    try:
        result_frame = json.loads(flux_variability_analysis(
            cobra_model, reaction_list, loopless, fraction_of_optimum, pfba_factor).to_json())
        result = {
            'minimum': [{'name': name, 'value': value} for name, value in result_frame['minimum'].items()],
            'maximum': [{'name': name, 'value': value} for name, value in result_frame['maximum'].items()],
        }
    except Exception as error:
        error_result = report_cobra_computation_error(error)
        app.send_task(**get_result_kwargs('fba', pk, error_result, is_error=True))
        return
    app.send_task(**get_result_kwargs('fva', pk, result))
