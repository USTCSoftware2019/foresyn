from django.db import models
import cobra


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
            self.identifier, self.name, self.subsystem, self.lower_bound, self.upper_bound, self.objective_coefficient)
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
        cobra_model.add_reactions([reaction.build() for reaction in self.reactions.all()])
        cobra_model.objective = self.objective
        return cobra_model

    def json(self):
        return dict(
            **{field: getattr(self, field) for field in ['identifier', 'name', 'objective']},
            reactions=list([reaction.id for reaction in self.reactions.all()])
        )
