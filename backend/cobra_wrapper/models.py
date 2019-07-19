from django.db import models
from django.utils.translation import gettext as _
import cobra


# class CobraMetabolite(models.Model):
#     base = models.CharField(max_length=50)
#     formula = models.CharField(max_length=50)
#     name = models.CharField(max_length=50)
#     compartment = models.CharField(max_length=50)

#     class Meta:
#         verbose_name = _("cobra metabolite")
#         verbose_name_plural = _("cobra metabolites")

#     def __str__(self):
#         return self.id + ' ' + self.name

#     def build(self):
#         return cobra.Metabolite(
#             self.base, formula=self.formula, name=self.name,
#             compartment=self.compartment)


# class CobraReaction(models.Model):
#     base = models.CharField(max_length=50)
#     name = models.CharField(max_length=50)
#     subsystem = models.CharField(max_length=50)
#     lower_bound = models.IntegerField(default=0)
#     upper_bound = models.IntegerField(default=1000)
#     metabolites = models.ManyToManyField(CobraMetabolite)
#     coefficients = models.CharField(max_length=255)
#     genes = models.models.TextField()

#     class Meta:
#         verbose_name = _("cobra reaction")
#         verbose_name_plural = _("cobra reactions")

#     def __str__(self):
#         return self.id + ' ' + self.name

#     def build(self):
#         cobra_reaction = cobra.Reaction(self.base)
#         cobra_reaction.name = self.name
#         cobra_reaction.subsystem = self.subsystem
#         cobra_reaction.lower_bound = self.lower_bound
#         cobra_reaction.upper_bound = self.upper_bound
#         cobra_reaction.add_metabolites(dict(
#             zip(
#                 [metabolite.build() for metabolite in self.metabolites],
#                 self.coefficients.split()
#             )
#         ))
#         cobra_reaction.gene_reaction_rule = self.genes
#         return cobra_reaction


# class CobraModel(models.Model):
#     base = models.CharField(max_length=50)
#     reactions = models.ManyToManyField(CobraReaction)
#     # json to metabolites and their stoichiometric coefficients
#     objective = models.CharField(max_length=50)

#     class Meta:
#         verbose_name = _("cobra model")
#         verbose_name_plural = _("cobra models")

#     def __str__(self):
#         return self.id

#     def build(self):
#         cobra_model = cobra.Model(self.base)
#         cobra_model.add_reactions(
#             [reaction.build() for reaction in self.reactions])
#         cobra_model.objective = self.objective
#         return cobra_model
