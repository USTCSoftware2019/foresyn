from cobra.flux_analysis import flux_variability_analysis
from celery import shared_task


@shared_task
def cobra_fba(cobra_model):
    return cobra_model.optimize()


@shared_task
def cobra_fva(cobra_model, reaction_list=None, loopless=False, fraction_of_optimum=1.0, pfba_factor=None):
    return flux_variability_analysis(cobra_model, reaction_list, loopless, fraction_of_optimum, pfba_factor)
