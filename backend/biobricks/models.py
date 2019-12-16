from django.db import models


class Biobrick(models.Model):
    part_name = models.CharField(unique=True, max_length=127)
    description = models.TextField(null=True)
    keywords = models.TextField(null=True)
    uses = models.IntegerField(null=True)
