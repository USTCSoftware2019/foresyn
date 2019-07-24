import json

from django.db import models
from django.contrib.auth.models import User
import cobra

from .utils import get_required_fields


class CobraMetabolite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    formula = models.CharField(max_length=50, blank=True, default='')
    name = models.CharField(max_length=50, blank=True, default='')
    charge = models.CharField(max_length=50, blank=True, null=True, default=None)
    compartment = models.CharField(max_length=50, blank=True, null=True, default=None)
    plain_fields = ['identifier', 'formula', 'name', 'charge', 'compartment']

    def build(self):
        return cobra.Metabolite(self.identifier, **get_required_fields(self, self.plain_fields[1:]))

    def json(self):
        return get_required_fields(self, self.plain_fields)


class CobraReaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    subsystem = models.CharField(max_length=50, blank=True, default='')
    lower_bound = models.FloatField(default=0.0)
    upper_bound = models.FloatField(blank=True, null=True, default=None)
    objective_coefficient = models.FloatField(default=0.0)
    metabolites = models.ManyToManyField(CobraMetabolite)
    coefficients = models.CharField(max_length=255, blank=True, default='')
    gene_reaction_rule = models.CharField(max_length=255, blank=True, default='')
    plain_fields = [
        'identifier', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'gene_reaction_rule'
    ]

    def build(self):
        cobra_reaction = cobra.Reaction(self.identifier, **get_required_fields(self, self.plain_fields[1:-2]))
        cobra_reaction.add_metabolites(dict(zip(
            [metabolite.build() for metabolite in self.metabolites.all()],
            [float(coefficient) for coefficient in self.coefficients.split()]
        )))
        cobra_reaction.gene_reaction_rule = self.gene_reaction_rule
        return cobra_reaction

    def json(self):
        return dict(
            **get_required_fields(self, self.plain_fields),
            metabolites=[metabolite.id for metabolite in self.metabolites.all()],
            coefficients=[float(coefficient) for coefficient in self.coefficients.split()]
        )


class CobraModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    reactions = models.ManyToManyField(CobraReaction)
    objective = models.CharField(max_length=50, default='')
    plain_fields = ['identifier', 'name', 'objective']

    def build(self):
        cobra_model = cobra.Model(self.identifier, **get_required_fields(self, self.plain_fields[1:-1]))
        for reaction in self.reactions.all():
            cobra_reaction = reaction.build()
            cobra_model.add_reaction(cobra_reaction)
            cobra_reaction.objective_coefficient = reaction.objective_coefficient
        cobra_model.objective = self.objective
        return cobra_model

    def json(self):
        return dict(
            **get_required_fields(self, self.plain_fields),
            reactions=list([reaction.id for reaction in self.reactions.all()])
        )

    def fba(self):
        solution = self.build().optimize()
        return {
            'objective_value': solution.objective_value,
            'status': solution.status,
            'fluxes': json.loads(solution.fluxes.to_json()),
            'shadow_prices': json.loads(solution.shadow_prices.to_json())
        }

    def fva(self, **kwarg):  # Param checking is done by views
        return json.loads(cobra.flux_analysis.flux_variability_analysis(self.build(), **kwarg).to_json())
