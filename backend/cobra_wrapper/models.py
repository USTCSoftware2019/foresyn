import json

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
import cobra


class CobraModel(models.Model):
    sbml_content = models.TextField()
    name = models.CharField(max_length=127)
    objective = models.CharField(max_length=50)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'model'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobramodel_detail', kwargs={'pk': self.pk})

    def build(self):
        return cobra.io.read_sbml_model(self.sbml_content)


def validate_json_str_or_blank_str(value):
    if value:
        try:
            json.loads(value)
        except ValueError:
            raise ValidationError('%(value)s is neither a blank str nor a json str', params={'value': value})


class CobraFba(models.Model):
    desc = models.TextField(blank=True, default='')

    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, default='', validators=[validate_json_str_or_blank_str])

    class Meta:
        verbose_name = 'fba'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fba]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafba_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraFva(models.Model):
    desc = models.TextField(blank=True, default='')
    reaction_list = models.TextField()
    loopless = models.BooleanField(default=False)
    fraction_of_optimum = models.FloatField(default=1.0)
    pfba_factor = models.BooleanField(blank=True)

    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, default='', validators=[validate_json_str_or_blank_str])

    class Meta:
        verbose_name = 'fva'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fva]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafva_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraModelChange(models.Model):
    # When `fields` is blank, the change is actually a creation record of the model
    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE)
    fields = models.CharField(max_length=200, blank=True)
    previous_values = models.TextField(blank=True)
    values = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'model_change'
        ordering = ['-time']

    def __str__(self):
        """Use the method to get shown text of the change"""
        if self.fields:
            return '{} is changed from {} to {}'.format(self.fields, self.previous_values, self.values)
        else:
            return 'created'
