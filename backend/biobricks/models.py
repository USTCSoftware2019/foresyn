from django.db import models


class Biobrick(models):
    part_name = models.CharField(unique=True, max_length=127)
    description = models.TextField()
    keywords = models.TextField()
    uses = models.IntegerField()
