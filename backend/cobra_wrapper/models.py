import json

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
import cobra

from .utils import load_sbml


class CobraModel(models.Model):
    sbml_content = models.TextField()
    name = models.CharField(max_length=200)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'model'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobramodel_detail', kwargs={'pk': self.pk})

    def build(self):
        cobra_model: cobra.Model = load_sbml(self.sbml_content)
        cobra_model.name = self.name
        return cobra_model


def validate_json_str_or_blank_str(value):
    if value:
        try:
            json.loads(value)
        except ValueError:
            raise ValidationError('%(value)s is neither a blank str nor a json str', params={'value': value})


class CobraFba(models.Model):
    desc = models.TextField(blank=True)

    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE, related_name='fba_list')
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, validators=[validate_json_str_or_blank_str])

    class Meta:
        verbose_name = 'fba'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fba]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafba_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraFva(models.Model):
    desc = models.TextField(blank=True)
    reaction_list = models.TextField()
    loopless = models.BooleanField(default=False)
    fraction_of_optimum = models.FloatField(default=1.0)
    pfba_factor = models.BooleanField(blank=True)

    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE, related_name='fva_list')
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, validators=[validate_json_str_or_blank_str])

    class Meta:
        verbose_name = 'fva'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fva]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafva_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraModelChange(models.Model):
    change_type = models.CharField(max_length=50, choices=[
        ('created', 'created'),
        ('add_reaction', 'add_reaction'),
        ('del_reaction', 'del_reaction'),
        ('sbml_content', 'sbml_content'),
        ('name', 'name'),
        ('objective', 'objective'),
    ])
    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE, related_name='changes')
    # pre_sbml_content = models.TextField(blank=True)  # The field may take much memory and disk space
    # `pre_info` is deleted reaction id, pre name or pre objective
    # The same to `new_info`, but it could also be new reaction id
    pre_info = models.CharField(max_length=600, blank=True)
    new_info = models.CharField(max_length=600, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    SHOWN_TEXT_TEMPLATE_CHOICES = {
        'created': 'Created',
        'add-reaction': 'Add reaction {new_info}',
        'del-reaction': 'Delete reaction {pre_info}',
        'sbml-content': 'Use new SBML file',
        'name': 'Change name from {pre_info} to {new_info}',
        'objective': 'Change objective to {new_info}',
    }

    class Meta:
        verbose_name = 'model_change'
        ordering = ['-created_time']

    def __str__(self):
        """Use the method to get shown text of the change"""
        return self.SHOWN_TEXT_TEMPLATE_CHOICES[self.change_type].format(
            pre_info=self.pre_info, new_info=self.new_info)
