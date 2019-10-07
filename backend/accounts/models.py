from django.contrib.auth.models import User
from django.db import models
from bigg_database.models import Model, Metabolite, Gene, Reaction


class PackModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)


class PackReaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)


class PackGene(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Gene, on_delete=models.CASCADE)


class PackMetabolite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Metabolite, on_delete=models.CASCADE)

# TO-DO: biobricks
