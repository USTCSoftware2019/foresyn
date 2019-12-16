from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from bigg_database.models import Model, Metabolite, Gene, Reaction
from cobra_wrapper.models import CobraModel as ComputationalModel
from biobricks.models import Biobrick


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')
