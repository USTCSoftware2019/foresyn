from django.contrib.auth.models import User
from django.db import models
from bigg_database.models import Model, Metabolite, Gene, Reaction
from cobra_wrapper.models import CobraModel as ComputationalModel
from biobricks.models import Biobrick


class PackModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)


class PackReaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)


class PackGene(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)


class PackMetabolite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metabolite = models.ForeignKey(Metabolite, on_delete=models.CASCADE)


class PackComputationalModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='model')
    model = models.ForeignKey(ComputationalModel, on_delete=models.CASCADE)


class PackBiobrick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    biobrick = models.ForeignKey(Biobrick, on_delete=models.CASCADE)
