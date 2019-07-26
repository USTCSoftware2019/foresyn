import json

from django.db import models, connection
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import cobra

try:
    if connection.vendor == 'postgresql':
        from django.contrib.postgres.fields import JSONField
    else:
        from bigg_database.fields import JSONField
except ImportError:
    class JSONField(models.TextField):
        description = "JSON"

        def from_db_value(self, value, expression, connection):
            if value is None:
                return value
            return json.loads(value)

        def to_python(self, value):
            if value is None or not isinstance(value, str):
                return value
            else:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    raise ValidationError

        def get_prep_value(self, value):
            return json.dumps(value)

        def value_to_string(self, obj):
            value = self.value_from_object(obj)
            return self.get_prep_value(value)


def get_fields(obj, fields):
    return {field: getattr(obj, field) for field in fields}


def convert_cobra_id(info):
    info['id'] = info['cobra_id']
    info.pop('cobra_id')
    return info


class AutoCleanModel(models.Model):
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class CobraMetabolite(AutoCleanModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    formula = models.CharField(max_length=50, blank=True, default='')
    charge = models.CharField(max_length=50, blank=True, null=True, default=None)
    compartment = models.CharField(max_length=50, blank=True, null=True, default=None)

    def json(self):
        return get_fields(self, ['id', 'cobra_id', 'name', 'formula', 'charge', 'compartment'])

    def build(self):
        return cobra.Metabolite(**convert_cobra_id(self.json()))


class CobraReaction(AutoCleanModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    subsystem = models.CharField(max_length=50, blank=True, default='')
    lower_bound = models.FloatField(default=0.0)
    upper_bound = models.FloatField(blank=True, null=True, default=None)
    objective_coefficient = models.FloatField(default=0.0)
    metabolites = models.ManyToManyField(CobraMetabolite)
    coefficients = JSONField(default=[])  # FIXME
    gene_reaction_rule = models.TextField(blank=True, default='')

    def json(self):
        return dict(
            **get_fields(self, [
                'id', 'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient',
                'coefficients', 'gene_reaction_rule'
            ]),
            metabolites=[metabolite.id for metabolite in self.metabolites.all()]
        )

    def build(self):
        reaction_init = convert_cobra_id(self.json())
        for field in ['metabolites', 'coefficients', 'objective_coefficient', 'gene_reaction_rule']:
            reaction_init.pop(field)
        cobra_reaction = cobra.Reaction(**reaction_init)
        cobra_reaction.add_metabolites(
            dict(zip([metabolite.build() for metabolite in self.metabolites.all()], self.coefficients)))
        cobra_reaction.gene_reaction_rule = self.gene_reaction_rule
        return cobra_reaction


class CobraModel(AutoCleanModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    reactions = models.ManyToManyField(CobraReaction)
    objective = models.CharField(max_length=50, default='')

    def json(self):
        return dict(
            **get_fields(self, ['id', 'cobra_id', 'name', 'objective']),
            reactions=[reaction.id for reaction in self.reactions.all()]
        )

    def build(self):
        model_init = convert_cobra_id(self.json())
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
