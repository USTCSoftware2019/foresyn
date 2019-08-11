import json

import cobra
from celery import shared_task


@shared_task
def fba(model):
    solution = model.build().optimize()
    return {
        'objective_value': solution.objective_value,
        'status': solution.status,
        'fluxes': json.loads(solution.fluxes.to_json()),
        'shadow_prices': json.loads(solution.shadow_prices.to_json())
    }


@shared_task
def fva(model, reaction_list=None, loopless=False, fraction_of_optimum=1.0, pfba_factor=None):
    reaction_list = [reaction.build() for reaction in reaction_list] if reaction_list else None
    return json.loads(cobra.flux_analysis.flux_variability_analysis(
        model.build(), reaction_list, loopless, fraction_of_optimum, pfba_factor
    ).to_json())
