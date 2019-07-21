from django.db import models
import cobra
from cobra.flux_analysis import flux_variability_analysis


class CobraMetabolite(models.Model):
    """
    @see cobra.Metabolite
    """
    identifier = models.CharField(max_length=50)
    formula = models.CharField(max_length=50, blank=True, default='')
    name = models.CharField(max_length=50, blank=True, default='')
    charge = models.CharField(max_length=50, blank=True, null=True, default=None)
    compartment = models.CharField(max_length=50, blank=True, null=True, default=None)

    def build(self):
        return cobra.Metabolite(self.identifier, self.formula, self.name, self.charge, self.compartment)

    def json(self):
        return dict(**{field: getattr(self, field) for field in [
            'identifier', 'formula', 'name', 'charge', 'compartment']})

    def fba(self, verbose=False):
        cobra_model = self.build()
        if verbose:
            solution = cobra_model.optimize()
            return {
                'objective_value': solution.objective_value,
                'status': solution.status,
                'fluxes': solution.fluxes.to_json(),
                'shadow_prices': solution.shadow_prices.to_json()
            }
        else:
            pass  # todo

    def fva(self, verbose=False, **kwarg):
        cobra_model = self.build()
        if verbose:
            return flux_variability_analysis(cobra_model, **kwarg).to_json()
        else:
            pass  # todo


class CobraReaction(models.Model):
    identifier = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    subsystem = models.CharField(max_length=50, blank=True, default='')
    lower_bound = models.FloatField(default=0.0)
    upper_bound = models.FloatField(blank=True, null=True, default=None)
    objective_coefficient = models.FloatField(default=0.0)
    metabolites = models.ManyToManyField(CobraMetabolite)
    coefficients = models.CharField(max_length=255, blank=True, default='')
    gene_reaction_rule = models.CharField(max_length=255, blank=True, default='')

    def build(self):
        cobra_reaction = cobra.Reaction(
            self.identifier, self.name, self.subsystem, self.lower_bound, self.upper_bound)
        cobra_reaction.add_metabolites(dict(zip(
            [metabolite.build() for metabolite in self.metabolites.all()],
            [float(coefficient) for coefficient in self.coefficients.split()]
        )))
        cobra_reaction.gene_reaction_rule = self.gene_reaction_rule
        return cobra_reaction

    def json(self):
        return dict(
            **{field: getattr(self, field) for field in [
                'identifier', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient',
                'gene_reaction_rule'
            ]},
            metabolites=list([metabolite.id for metabolite in self.metabolites.all()]),
            coefficients=list([float(coefficient) for coefficient in self.coefficients.split()])
        )


class CobraModel(models.Model):
    identifier = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    reactions = models.ManyToManyField(CobraReaction)
    objective = models.CharField(max_length=50)

    def build(self):
        cobra_model = cobra.Model(self.identifier, self.name)
        for reaction in self.reactions.all():
            cobra_reaction = reaction.build()
            cobra_model.add_reaction(cobra_reaction)
            cobra_reaction.objective_coefficient = reaction.objective_coefficient
        cobra_model.objective = self.objective
        return cobra_model

    def json(self):
        return dict(
            **{field: getattr(self, field) for field in ['identifier', 'name', 'objective']},
            reactions=list([reaction.id for reaction in self.reactions.all()])
        )
