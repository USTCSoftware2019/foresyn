import cobra
from cobra.flux_analysis import flux_variability_analysis

from .celery import app


@app.task
def cobra_fba(pk, cobra_model_json):
    cobra_model = cobra.io.from_json(cobra_model_json)
    result = cobra_model.optimize().to_frame().to_json()
    app.send_task(
        'cobra_wrapper.tasks.cobra_fba_save',
        args=[pk, result, app.current_task.request.id],
        kwargs={},
        queue='cobra_results',
        routing_key='cobra_result.fba'
    )


@app.task
def cobra_fva(pk, cobra_model_json, reaction_list=None, loopless=False, fraction_of_optimum=1.0, pfba_factor=None):
    cobra_model = cobra.io.from_json(cobra_model_json)
    result = flux_variability_analysis(
        cobra_model, reaction_list, loopless, fraction_of_optimum, pfba_factor
    ).to_json()
    app.send_task(
        'cobra_wrapper.tasks.cobra_fva_save',
        args=[pk, result, app.current_task.request.id],
        kwargs={},
        queue='cobra_results',
        routing_key='cobra_result.fva'
    )
