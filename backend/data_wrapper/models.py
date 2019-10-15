from django.db import models
from bigg_database.models import Model


# Create your models here.
class DataModel(models.Model):
    bigg_id = models.CharField(max_length=127)
    sbml_content = models.TextField()