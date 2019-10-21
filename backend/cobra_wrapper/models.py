import json

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
import cobra

from .utils import load_sbml, dump_sbml, restore_reaction_by_json


class CobraModel(models.Model):
    sbml_content = models.TextField()
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=200, blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    reactions = models.TextField(blank=True)
    metabolites = models.TextField(blank=True)
    genes = models.TextField(blank=True)

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

    def cache(self, cobra_model: cobra.Model):
        self.reactions = json.dumps([{'cobra_id': reaction.id, 'name': reaction.name}
                                     for reaction in cobra_model.reactions])
        self.metabolites = json.dumps([{'cobra_id': metabolite.id, 'name': metabolite.name}
                                       for metabolite in cobra_model.metabolites])
        self.genes = json.dumps([{'cobra_id': gene.id, 'name': gene.name} for gene in cobra_model.genes])
        self.save()


def validate_json_str_or_blank_str(value):
    if value:
        try:
            json.loads(value)
        except ValueError:
            raise ValidationError('%(value)s is neither a blank str nor a json str', params={'value': value})


class CobraFba(models.Model):
    desc = models.CharField(max_length=600, blank=True)
    deleted_genes = models.TextField(blank=True)

    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE, related_name='fba_list')
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, validators=[validate_json_str_or_blank_str])
    ok = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'fba'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fba]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafba_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraRgeFba(models.Model):
    desc = models.CharField(max_length=600, blank=True)
    deleted_genes = models.TextField(blank=True)

    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE, related_name='rgefba_list')
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, validators=[validate_json_str_or_blank_str])
    ok = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'rge_fba'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fba]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrargefba_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraFva(models.Model):
    desc = models.CharField(max_length=600, blank=True)
    reaction_list = models.TextField()
    loopless = models.BooleanField(default=False)
    fraction_of_optimum = models.FloatField(default=1.0)
    pfba_factor = models.FloatField(default=1.0)
    deleted_genes = models.TextField(blank=True)

    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE, related_name='fva_list')
    start_time = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(null=True, blank=True, default=None)
    result = models.TextField(blank=True, validators=[validate_json_str_or_blank_str])
    ok = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'fva'
        ordering = ['-start_time']

    def __str__(self):
        return '{}[fva]'.format(self.desc)

    def get_absolute_url(self):
        return reverse('cobra_wrapper:cobrafva_detail', kwargs={'model_pk': self.model.pk, 'pk': self.pk})


class CobraModelChange(models.Model):
    change_type = models.CharField(max_length=50, choices=[
        ('add_reaction', 'add_reaction'),
        ('del_reaction', 'del_reaction'),
    ])
    model = models.ForeignKey(CobraModel, on_delete=models.CASCADE, related_name='changes')
    reaction_info = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'model_change'
        ordering = ['-created_time']

    def __str__(self):
        """Use the method to get shown text of the change"""
        reactions = json.loads(self.reaction_info)['reactions']
        return '{} {} {}'.format(
            ', '.join(['"' + reaction['name'] + '"' for reaction in reactions]),
            'are' if len(reactions) > 1 else 'is',
            'added' if self.change_type == 'add_reaction' else 'deleted')

    def get_type_name(self):
        return {
            'del_reaction': 'Delete reactions',
            'add_reaction': 'Add reactions',
        }[self.change_type]

    def restore(self, name: str, desc: str = '') -> CobraModel:
        changes = CobraModelChange.objects.filter(model=self.model, created_time__gt=self.created_time)
        cobra_model = self.model.build()
        for change in changes:
            reaction_info = json.loads(change.reaction_info)
            if change.change_type == 'add_reaction':
                cobra_model.remove_reactions([reaction_info['cobra_id']])
            elif change.change_type == 'del_reaction':
                reactions = [restore_reaction_by_json(cobra_model, info) for info in reaction_info['reactions']]
                cobra_model.add_reactions(reactions)
        new_model = CobraModel.objects.create(name=name, desc=desc, sbml_content=dump_sbml(cobra_model),
                                              owner=self.model.owner)
        new_model.cache(cobra_model)
        return new_model
