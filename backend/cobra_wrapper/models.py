import json

from django.db import models
from django.contrib.auth.models import User
import cobra


def get_fields(obj, fields):
    return {field: getattr(obj, field) for field in fields}


class CobraMetabolite(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    formula = models.CharField(max_length=50, blank=True, default='')
    charge = models.CharField(max_length=50, blank=True, null=True, default=None)
    compartment = models.CharField(max_length=50, blank=True, null=True, default=None)

    def json(self):
        return get_fields(self, ['id', 'name', 'formula', 'charge', 'compartment'])

    def build(self):
        return cobra.Metabolite(**self.json())


class CobraReaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    subsystem = models.CharField(max_length=50, blank=True, default='')
    lower_bound = models.FloatField(default=0.0)
    upper_bound = models.FloatField(blank=True, null=True, default=None)
    objective_coefficient = models.FloatField(default=0.0)
    metabolites = models.ManyToManyField(CobraMetabolite)
    coefficients = models.TextField()
    gene_reaction_rule = models.TextField()

    def json(self):
        return dict(
            **get_fields(self, [
                'id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'gene_reaction_rule'
            ]),
            metabolites=[metabolite.id for metabolite in self.metabolites.all()],
            coefficients=[float(coefficient) for coefficient in self.coefficients.split()]
        )

    def build(self):
        reaction_init = self.json()
        for field in ['metabolites', 'coefficients', 'objective_coefficient', 'gene_reaction_rule']:
            reaction_init.pop(field)
        cobra_reaction = cobra.Reaction(**reaction_init)
        cobra_reaction.add_metabolites(dict(zip(
            [metabolite.build() for metabolite in self.metabolites.all()],
            [float(coefficient) for coefficient in self.coefficients.split()]
        )))
        cobra_reaction.gene_reaction_rule = self.gene_reaction_rule
        return cobra_reaction


class CobraModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    reactions = models.ManyToManyField(CobraReaction)
    objective = models.CharField(max_length=50, default='')

    def json(self):
        return dict(
            **get_fields(self, ['id', 'name', 'objective']),
            reactions=[reaction.id for reaction in self.reactions.all()]
        )

    def build(self):
        model_init = self.json()
        model_init.pop('reactions')
        cobra_model = cobra.Model(model_init)
        for reaction in self.reactions.all():
            cobra_reaction = reaction.build()
            cobra_model.add_reaction(cobra_reaction)
            cobra_reaction.objective_coefficient = reaction.objective_coefficient
        cobra_model.objective = self.objective
        return cobra_model

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
