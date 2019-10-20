import json
import re
from typing import List

from django import forms
import cobra

from . import models
from .utils import dump_sbml, get_reaction_json

# TODO(myl7): Validation layer


class CleanSbmlContentMixin:
    def clean(self: forms.Form):
        cleaned_data = super().clean()
        sbml_content = cleaned_data['sbml_content'].read()

        if isinstance(sbml_content, bytes):
            try:
                sbml_content = sbml_content.decode('utf-8')
            except UnicodeDecodeError:
                self.add_error('sbml_content', 'Can not decode SBML file with UTF-8')
                return cleaned_data

        try:
            cobra.io.validate_sbml_model(sbml_content)
        except cobra.io.sbml.CobraSBMLError:
            self.add_error('sbml_content', 'validation for SBML file failed')
            return cleaned_data

        cleaned_data['sbml_content'] = sbml_content
        return cleaned_data


class CobraModelCreateForm(CleanSbmlContentMixin, forms.Form):
    sbml_content = forms.FileField()
    name = forms.CharField(max_length=200, min_length=1)
    desc = forms.CharField(max_length=200, required=False)

    def save(self, owner):
        if not self.is_valid():
            raise ValueError()
        return models.CobraModel.objects.create(name=self.cleaned_data['name'], desc=self.cleaned_data['desc'],
                                                sbml_content=self.cleaned_data['sbml_content'], owner=owner)


class CobraModelNameUpdateForm(forms.Form):
    name = forms.CharField(max_length=200, min_length=1)
    desc = forms.CharField(max_length=200, required=False)
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='name')

    def save(self, model):
        if not self.is_valid():
            raise ValueError()
        model.name = self.cleaned_data['name']
        model.desc = self.cleaned_data['desc']
        model.save()
        return model


class CobraModelObjectiveUpdateForm(forms.Form):
    objective = forms.CharField(min_length=1)
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='objective')

    def save(self, model):
        if self.errors:
            raise ValueError()
        cobra_model: cobra.Model = model.build()
        cobra_model.objective = self.cleaned_data['objective']
        model.sbml_content = dump_sbml(cobra_model)
        model.save()
        return model


class CobraModelReactionDeleteForm(forms.Form):
    deleted_reaction_id = forms.CharField(min_length=1)
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='del_reaction')

    def save(self, model):
        if self.errors:
            raise ValueError()
        cobra_model: cobra.Model = model.build()
        deleted_reaction_id_list = self.cleaned_data['deleted_reaction_id'].split(',')
        deleted_reaction_info = {
            'reactions': [
                get_reaction_json(cobra_model.reactions.get_by_id(reaction_id))
                for reaction_id in deleted_reaction_id_list
            ],
        }
        models.CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                               reaction_info=json.dumps(deleted_reaction_info))
        cobra_model.remove_reactions(deleted_reaction_id_list)
        model.sbml_content = dump_sbml(cobra_model)
        model.save()
        return model


class CobraModelReactionCreateForm(forms.Form):
    cobra_id = forms.CharField(max_length=600)
    name = forms.CharField(max_length=600)
    subsystem = forms.CharField(max_length=200)
    lower_bound = forms.FloatField(initial=0.0)
    upper_bound = forms.FloatField(initial=1000.0)
    reaction_str = forms.CharField()
    gene_reaction_rule = forms.CharField()
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='add_reaction')

    def save(self, model):
        if self.errors:
            raise ValueError()
        cobra_model: cobra.Model = model.build()
        cobra_reaction = cobra.Reaction(id=self.cleaned_data['cobra_id'], name=self.cleaned_data['name'],
                                        subsystem=self.cleaned_data['subsystem'],
                                        lower_bound=self.cleaned_data['lower_bound'],
                                        upper_bound=self.cleaned_data['upper_bound'])
        cobra_model.add_reactions([cobra_reaction])
        cobra_reaction.reaction = self.cleaned_data['reaction_str']
        cobra_reaction.gene_reaction_rule = self.cleaned_data['gene_reaction_rule']
        models.CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                               reaction_info=json.dumps({
                                                   'reactions': [get_reaction_json(cobra_reaction)],
                                               }))
        model.sbml_content = dump_sbml(cobra_model)
        model.save()
        return model


cobra_model_update_forms = {
    'name': CobraModelNameUpdateForm,
    'objective': CobraModelObjectiveUpdateForm,
    'del_reaction': CobraModelReactionDeleteForm,
    'add_reaction': CobraModelReactionCreateForm,
}


def clean_comma_separated_str(form, value: str) -> str:
    return ','.join([item.strip() for item in value.split(',') if re.fullmatch(r'[a-zA-Z0-9_-]+', item.strip())])


def load_comma_separated_str(value: str) -> List[str]:
    return value.split(',') if value else []


class CobraModelChangeRestoreForm(forms.Form):
    name = forms.CharField(max_length=200, min_length=1)
    desc = forms.CharField(max_length=200, required=False)


class CleanDeletedGenesMixin:
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['deleted_genes'] = clean_comma_separated_str(self, cleaned_data.get('deleted_genes', ''))
        return cleaned_data


class CobraFvaForm(CleanDeletedGenesMixin, forms.ModelForm):
    class Meta:
        model = models.CobraFva
        fields = ['desc', 'reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor', 'deleted_genes']

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['reaction_list'] = clean_comma_separated_str(self, cleaned_data.get('reaction_list', ''))
        return cleaned_data
