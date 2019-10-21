from django.contrib.auth import get_user_model
from django.db import models

from cobra_wrapper.models import CobraModel

User = get_user_model()


class OneTimeShareLink(models.Model):
    key = models.CharField(max_length=127)
    shared_type = models.CharField(max_length=15)
    shared_id = models.CharField(max_length=127)


class ShareModel(models.Model):
    sbml_content = models.TextField()
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=200, blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    reactions = models.TextField(blank=True)
    metabolites = models.TextField(blank=True)
    genes = models.TextField(blank=True)
