from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db import models

# Create your models here.
from cobra_wrapper.models import CobraMetabolite, CobraModel, CobraReaction

User = get_user_model()


class OneTimeShareLink(models.Model):
    key = models.CharField(max_length=127)
    shared_type = models.CharField(max_length=15)
    shared_id = models.CharField(max_length=127)


class ShareAuthorization(models.Model):
    public = models.BooleanField()
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class AbstractBaseShare(models.Model):
    can_edit = models.BooleanField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # default=None, blank=False. Just to populate existing database
    auth = models.ForeignKey(ShareAuthorization, on_delete=models.CASCADE, default=None)

    class Meta:
        abstract = True


# Change OneToOne to OneToMany, as there may be several shares related to one model.
# E.g., user may create a private share link during development. And after completing it,
# user may want to make it public.
class ModelShare(AbstractBaseShare):
    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE)

    reactions = models.ManyToManyField('ReactionShare')


class ReactionShare(AbstractBaseShare):
    reaction = models.ForeignKey(CobraReaction, on_delete=models.CASCADE)

    metabolites = models.ManyToManyField('MetaboliteShare')


class MetaboliteShare(AbstractBaseShare):
    metabolite = models.ForeignKey(CobraMetabolite, on_delete=models.CASCADE)
