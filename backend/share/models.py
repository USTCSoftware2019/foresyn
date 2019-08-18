from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from cobra_wrapper.models import CobraMetabolite, CobraModel, CobraReaction

User = get_user_model()


class ModelShare(models.Model):
    model = models.OneToOneField(CobraModel, on_delete=models.CASCADE)
    public = models.BooleanField()
    can_edit = models.BooleanField()

    reactions = models.ManyToManyField('ReactionShare')

    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class ReactionShare(models.Model):
    reaction = models.OneToOneField(CobraReaction, on_delete=models.CASCADE)
    public = models.BooleanField()
    can_edit = models.BooleanField()

    metabolites = models.ManyToManyField('MetaboliteShare')

    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class MetaboliteShare(models.Model):
    metabolite = models.OneToOneField(CobraMetabolite, on_delete=models.CASCADE)
    public = models.BooleanField()
    can_edit = models.BooleanField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
