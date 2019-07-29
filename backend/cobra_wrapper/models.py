import json

from django.db import models, connection
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
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


class AutoCleanMixin:
    def save(self, *args, **kwargs):
        super().full_clean()
        return super().save(*args, **kwargs)


class CobraStrMixin:
    cobra_id = None
    name = None

    def __str__(self):
        if self.name:
            return '{} - {}'.format(self.cobra_id, self.name)
        else:
            return self.cobra_id


class CobraMetabolite(CobraStrMixin, AutoCleanMixin, models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    formula = models.CharField(max_length=50, blank=True, default='')
    charge = models.CharField(max_length=50, blank=True, null=True, default=None)
    compartment = models.CharField(max_length=50, blank=True, null=True, default=None)

    MODEL_NAME = 'metabolite'

    def get_list_url():
        return reverse('cobra_wrapper:metabolite_list')

    def get_absolute_url(self):
        return reverse("cobra_wrapper:metabolite_detail", kwargs={"pk": self.pk})

    def json(self):
        return get_fields(self, ['id', 'cobra_id', 'name', 'formula', 'charge', 'compartment'])

    def build(self):
        return cobra.Metabolite(**convert_cobra_id(self.json()))


def validate_coefficients_is_list(value):
    if not isinstance(value, (list, tuple)):
        raise ValidationError('the field requires list or tuple', 'invalid')


class CobraReaction(CobraStrMixin, AutoCleanMixin, models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    subsystem = models.CharField(max_length=50, blank=True, default='')
    lower_bound = models.FloatField(default=0.0)
    upper_bound = models.FloatField(blank=True, null=True, default=None)
    objective_coefficient = models.FloatField(default=0.0)
    metabolites = models.ManyToManyField(CobraMetabolite)
    coefficients = JSONField(default=[], validators=[validate_coefficients_is_list])
    gene_reaction_rule = models.TextField(blank=True, default='')

    MODEL_NAME = 'reaction'

    def get_list_url():
        return reverse('cobra_wrapper:reaction_list')

    def get_absolute_url(self):
        return reverse("cobra_wrapper:reaction_detail", kwargs={"pk": self.pk})

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

    def get_metabolites_and_coefficients(self):
        return zip(self.metabolites.all(), self.coefficients)


class CobraModel(CobraStrMixin, AutoCleanMixin, models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50, blank=True, default='')
    reactions = models.ManyToManyField(CobraReaction)
    objective = models.CharField(max_length=50, default='')

    MODEL_NAME = 'model'

    def get_list_url():
        return reverse('cobra_wrapper:model_list')

    def get_absolute_url(self):
        return reverse("cobra_wrapper:model_detail", kwargs={"pk": self.pk})

    def json(self):
        return dict(
            **get_fields(self, ['id', 'cobra_id', 'name', 'objective']),
            reactions=[reaction.id for reaction in self.reactions.all()]
        )

    def build(self):
        model_init = convert_cobra_id(self.json())
        model_init.pop('reactions')
        cobra_model = cobra.Model(model_init)
        reaction_list = []
        cobra_reaction_list = []
        temp_reaction_list = []
        for reaction in self.reactions.all():
            cobra_reaction = reaction.build()
            reaction_list.append((cobra_reaction, reaction))
        for reaction_pair in reaction_list:
            cobra_reaction_list.append(reaction_pair[0])
            temp_reaction_list.append(reaction_pair[1])
        cobra_model.add_reactions(cobra_reaction_list)
        i = 0
        for reaction in cobra_model.reactions:
            reaction.objective_coefficient = temp_reaction_list[i].objective_coefficient
            i += 1
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
