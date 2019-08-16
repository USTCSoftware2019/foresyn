import json

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
import cobra


class CobraMetabolite(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=511)
    name = models.CharField(max_length=511, blank=True, default='')
    formula = models.CharField(max_length=127)
    charge = models.FloatField()
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
            charge=self.charge,
            compartment=(self.compartment if self.compartment else None)
        )


def validate_coefficients_space_splited_text(value):
    for coefficient in value.split():
        try:
            float(coefficient)
        except ValueError:
            raise ValidationError('%(value)s in coefficients is not a float', params={'value': coefficient})


class CobraReaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=511)
    name = models.CharField(max_length=511, blank=True, default='')
    subsystem = models.CharField(max_length=127, blank=True, null=True, default='')
    lower_bound = models.FloatField(default=0.0)
    upper_bound = models.FloatField(blank=True, null=True, default=None)
    metabolites = models.ManyToManyField(CobraMetabolite, blank=True)
    coefficients = models.TextField(blank=True, default='', validators=[validate_coefficients_space_splited_text])
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


class CobraModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=127)
    name = models.CharField(max_length=127, blank=True, default='')
    reactions = models.ManyToManyField(CobraReaction, blank=True)
    objective = models.CharField(max_length=50, default='', blank=True)

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
        cobra_model.add_reactions([reaction.build() for reaction in self.reactions.all()])
        cobra_model.objective = self.objective
        return cobra_model


def validate_json_str_or_blank_str(value):
    if value:
        try:
            json.loads(value)
        except ValueError:
            raise ValidationError('%(value)s is neither a blank str nor a json str', params={'value': value})


class CobraFba(models.Model):
    desc = models.TextField(blank=True, default='')
    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, default='', validators=[validate_json_str_or_blank_str])

    class Meta:
        verbose_name = 'fba'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fba]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafba_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraFva(models.Model):
    desc = models.TextField(blank=True, default='')
    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE)
    reaction_list = models.ManyToManyField(CobraReaction, blank=True)
    loopless = models.BooleanField(default=False, blank=True)
    fraction_of_optimum = models.FloatField(default=1.0, blank=True)
    pfba_factor = models.NullBooleanField(default=None, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, default='', validators=[validate_json_str_or_blank_str])

    class Meta:
        verbose_name = 'fva'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fva]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafva_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})
