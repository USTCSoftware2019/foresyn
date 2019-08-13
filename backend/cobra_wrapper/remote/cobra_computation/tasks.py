import cobra
from cobra.flux_analysis import flux_variability_analysis

from .celery import app


@app.task
def cobra_fba(cobra_model_json):
    cobra_model = cobra.io.from_json(cobra_model_json)
    return cobra_model.optimize().to_frame().to_json()


@app.task
def cobra_fva(cobra_model_json, reaction_json_list=(), loopless=False, fraction_of_optimum=1.0, pfba_factor=None):
    cobra_model = cobra.io.from_json(cobra_model_json)
    reaction_list = [cobra.io.from_json(reaction_json) for reaction_json in reaction_json_list]
    return flux_variability_analysis(cobra_model, reaction_list, loopless, fraction_of_optimum, pfba_factor).to_json()
