from django.db import models


# Create your models here.
class Regulation(models.Model):
    bNum = models.CharField(max_length=15, unique=True)
    gene = models.CharField(max_length=15, unique=True)
    rule = models.CharField(max_length=127, null=True)
    reference = models.CharField(max_length=127, null=True)

    def __str__(self):
        return self.gene
