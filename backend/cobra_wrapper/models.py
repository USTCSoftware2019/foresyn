from django.db import models
import cobra


class CobraMetabolite(models.Model):
    base = models.CharField(max_length=50)
    formula = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    compartment = models.CharField(max_length=50)

    def build(self):
        return cobra.Metabolite(
            self.base,
            formula=self.formula, name=self.name, compartment=self.compartment
        )

    # ! 这是我之前写的方法，你们可以视需求启用 <myl7>
    # def json(self):
    #     return dict(**{field: getattr(self, field) for field in [
    #         'base', 'formula', 'name', 'compartment'
    #     ]})


class CobraReaction(models.Model):
    base = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    subsystem = models.CharField(max_length=50)
    lower_bound = models.IntegerField(default=0)
    upper_bound = models.IntegerField(default=1000)
    metabolites = models.ManyToManyField(CobraMetabolite)
    coefficients = models.CharField(max_length=255)
    gene_reaction_rule = models.CharField(max_length=255)

    def build(self):
        cobra_reaction = cobra.Reaction(self.base)
        cobra_reaction.name = self.name
        cobra_reaction.subsystem = self.subsystem
        cobra_reaction.lower_bound = self.lower_bound
        cobra_reaction.upper_bound = self.upper_bound
        cobra_reaction.add_metabolites(dict(zip(
            [metabolite.build() for metabolite in self.metabolites.all()],
            [float(coefficient) for coefficient in self.coefficients.split()]
        )))
        cobra_reaction.gene_reaction_rule = self.gene_reaction_rule
        return cobra_reaction

    # def json(self):
    #     metabolite_list = list(
    #         [metabolite.id for metabolite in self.metabolites.all()])
    #     return dict(**{field: getattr(self, field) for field in [
    #         'base', 'name', 'subsystem', 'lower_bound', 'upper_bound',
    #         'gene_reaction_rule'
    #     ]}, metabolites=metabolite_list)


class CobraModel(models.Model):
    base = models.CharField(max_length=50)
    reactions = models.ManyToManyField(CobraReaction)
    objective = models.CharField(max_length=50)

    def build(self):
        cobra_model = cobra.Model(self.base)
        cobra_model.add_reactions(
            [reaction.build() for reaction in self.reactions.all()])
        cobra_model.objective = self.objective
        return cobra_model

    # def json(self):
    #     reaction_list = list(
    #         [reaction.id for reaction in self.reactions.all()])
    #     return dict(**{field: getattr(self, field) for field in [
    #         'base', 'objective'
    #     ]}, reactions=reaction_list)
