import json

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
import cobra


class CobraMetabolite(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=511)
    name = models.CharField(max_length=511, blank=True, default='')
    formula = models.CharField(max_length=127, blank=True, default='')
    charge = models.CharField(max_length=50, blank=True, default='')
    compartment = models.CharField(max_length=50, blank=True, default='')

    MODEL_NAME = 'metabolite'

    def __str__(self):
        return '{}[{}]'.format(self.cobra_id, self.name)

    def get_list_url():
        return reverse('cobra_wrapper:metabolite_list')

    def get_absolute_url(self):
        return reverse("cobra_wrapper:metabolite_detail", kwargs={"pk": self.pk})

    def build(self):
        return cobra.Metabolite(
            self.cobra_id,
            name=self.name,
            formula=self.formula,
            charge=(self.charge if self.charge else None),
            compartment=(self.compartment if self.compartment else None)
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
    coefficients = models.TextField(default='', validators=[])  # TODO: Check same number
    gene_reaction_rule = models.TextField(blank=True, default='')

    MODEL_NAME = 'reaction'

    def __str__(self):
        return '{}[{}]'.format(self.cobra_id, self.name)

    def get_list_url():
        return reverse('cobra_wrapper:reaction_list')

    def get_absolute_url(self):
        return reverse("cobra_wrapper:reaction_detail", kwargs={"pk": self.pk})

    def build(self):
        cobra_reaction = cobra.Reaction(
            self.cobra_id,
            name=self.name,
            subsystem=self.subsystem,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound
        )
        cobra_reaction.add_metabolites(self.get_metabolites_and_coefficients())
        cobra_reaction.gene_reaction_rule = self.gene_reaction_rule
        return cobra_reaction

    def get_metabolites_and_coefficients(self):
        return dict(zip(
            [metabolite.build() for metabolite in self.metabolites.all()],
            [float(coefficient) for coefficient in self.coefficients.split()]
        ))

    @property
    def metabolites_and_coefficients(self):
        return dict(zip([metabolite for metabolite in self.metabolites.all()], self.coefficients))


class CobraModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cobra_id = models.CharField(max_length=127)
    name = models.CharField(max_length=127, blank=True, default='')
    reactions = models.ManyToManyField(CobraReaction, blank=True)
    objective = models.CharField(max_length=50, default='', blank=True)

    MODEL_NAME = 'model'

    def __str__(self):
        return '{}[{}]'.format(self.cobra_id, self.name)

    def get_list_url():
        return reverse('cobra_wrapper:model_list')

    def get_absolute_url(self):
        return reverse("cobra_wrapper:model_detail", kwargs={"pk": self.pk})

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

    def fba(self):
        solution = self.build().optimize()
        return {
            'objective_value': solution.objective_value,
            'status': solution.status,
            'fluxes': json.loads(solution.fluxes.to_json()),
            'shadow_prices': json.loads(solution.shadow_prices.to_json())
        }

    def fva(self, **kwarg):
        return json.loads(cobra.flux_analysis.flux_variability_analysis(self.build(), **kwarg).to_json())
