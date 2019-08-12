import json

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
import cobra
from django_celery_results.models import TaskResult


class CobraMetabolite(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=511)
    name = models.CharField(max_length=511, blank=True, default='')
    formula = models.CharField(max_length=127, blank=True, default='')
    charge = models.CharField(max_length=50, blank=True, default='')
    compartment = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        verbose_name = "metabolite"
        ordering = ['cobra_id', 'name']

    def __str__(self):
        return '{}[{}]'.format(self.cobra_id, self.name)

    def get_absolute_url(self):
        return reverse("cobra_wrapper:cobrametabolite_detail", kwargs={"pk": self.pk})

    def build(self):
        return cobra.Metabolite(
            self.cobra_id,
            name=self.name,
            formula=self.formula,
            charge=(self.charge if self.charge else None),
            compartment=(self.compartment if self.compartment else None)
        )


def validate_coefficients_space_splited_text(value):
    for coefficient in value.split():
        try:
            float(coefficient)
        except ValueError:
            raise ValidationError(
                '%(value)s in coefficients is not a float',
                params={'value': coefficient}
            )


class CobraReaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=511)
    name = models.CharField(max_length=511, blank=True, default='')
    subsystem = models.CharField(max_length=127, blank=True, null=True, default='')
    lower_bound = models.FloatField(default=0.0)
    upper_bound = models.FloatField(blank=True, null=True, default=None)
    objective_coefficient = models.FloatField(default=0.0)
    metabolites = models.ManyToManyField(CobraMetabolite, blank=True)
    coefficients = models.TextField(default='', validators=[validate_coefficients_space_splited_text])
    gene_reaction_rule = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = "reaction"
        ordering = ['cobra_id', 'name']

    def __str__(self):
        return '{}[{}]'.format(self.cobra_id, self.name)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrareaction_detail', kwargs={'pk': self.pk})

    def build(self):
        cobra_reaction = cobra.Reaction(
            self.cobra_id,
            name=self.name,
            subsystem=self.subsystem,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound
        )
        cobra_reaction.add_metabolites(self._get_metabolites_and_coefficients())
        cobra_reaction.gene_reaction_rule = self.gene_reaction_rule
        return cobra_reaction

    def get_metabolites_and_coefficients(self):
        """Used in templates"""
        return dict(zip(
            self.metabolites.all(),
            [float(coefficient) for coefficient in self.coefficients.split()]
        ))

    def _get_metabolites_and_coefficients(self):
        return dict(zip(
            [metabolite.build() for metabolite in self.metabolites.all()],
            [float(coefficient) for coefficient in self.coefficients.split()]
        ))

    @property
    def metabolites_and_coefficients(self):
        return dict(zip([metabolite for metabolite in self.metabolites.all()], self.coefficients))


class CobraFba(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    result = models.ForeignKey(TaskResult, on_delete=models.CASCADE, blank=True)

    class Meta:
        verbose_name = 'fba'
        ordering = ['result']

    def __str__(self):
        return '{}[fba]'.format(self.result)

    # def get_absolute_url(self):
    #     return reverse('cobra_wrapper:cobrafba_detail', kwargs={'pk': self.pk})

    def used_time(self):
        return self.result.date_done - self.start_time


class CobraFva(models.Model):
    reaction_list = models.ManyToManyField(CobraReaction, blank=True)
    loopless = models.BooleanField(default=False, blank=True)
    fraction_of_optimum = models.FloatField(default=1.0, blank=True)
    pfba_factor = models.NullBooleanField(default=None, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    result = models.ForeignKey(TaskResult, on_delete=models.CASCADE, blank=True)

    class Meta:
        verbose_name = 'fva'
        ordering = ['result']

    def __str__(self):
        return '{}[fva]'.format(self.result)

    # def get_absolute_url(self):
    #     return reverse('cobra_wrapper:cobrafva_detail', kwargs={'pk': self.pk})

    def used_time(self):
        return self.result.date_done - self.start_time


class CobraModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=127)
    name = models.CharField(max_length=127, blank=True, default='')
    reactions = models.ManyToManyField(CobraReaction, blank=True)
    objective = models.CharField(max_length=50, default='', blank=True)
    fba = models.ManyToManyField(CobraFba, blank=True)
    fva = models.ManyToManyField(CobraFva, blank=True)

    class Meta:
        verbose_name = 'model'
        ordering = ['cobra_id', 'name']

    def __str__(self):
        return '{}[{}]'.format(self.cobra_id, self.name)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobramodel_detail', kwargs={'pk': self.pk})

    def build(self):
        cobra_model = cobra.Model(
            self.cobra_id,
            name=self.name,
        )

        reaction_pairs = []
        for reaction in self.reactions.all():
            cobra_reaction = reaction.build()
            reaction_pairs.append((cobra_reaction, reaction))
        cobra_model.add_reactions(list(zip(*reaction_pairs))[0])

        for cobra_reaction, reaction in reaction_pairs:
            cobra_reaction.objective_coefficient = reaction.objective_coefficient

        cobra_model.objective = self.objective
        return cobra_model

    def fba(self):  # DEPRECATED(myl7)
        solution = self.build().optimize()
        return {
            'objective_value': solution.objective_value,
            'status': solution.status,
            'fluxes': json.loads(solution.fluxes.to_json()),
            'shadow_prices': json.loads(solution.shadow_prices.to_json())
        }

    def fva(self, **kwarg):  # DEPRECATED(myl7)
        if 'reaction_list' in kwarg.keys():
            kwarg['reaction_list'] = [reaction.build() for reaction in kwarg['reaction_list']]
        return json.loads(cobra.flux_analysis.flux_variability_analysis(self.build(), **kwarg).to_json())
