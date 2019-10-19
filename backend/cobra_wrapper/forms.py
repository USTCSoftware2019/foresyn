import json
import re
from typing import List, Dict, Any

from django import forms
import cobra

from .models import CobraModel, CobraFba, CobraFva, CobraModelChange
from .utils import dump_sbml


class InstanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        self.instance = instance

    def save(self):
        try:
            self.instance.save()
        except AttributeError:
            pass
        return self.instance


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


class CobraModelCreateForm(CleanSbmlContentMixin, InstanceForm):
    sbml_content = forms.FileField()
    name = forms.CharField(max_length=200)

    def save(self, owner=None):
        if owner:
            if not self.is_valid():
                raise ValueError()
            self.instance = CobraModel.objects.create(name=self.cleaned_data['name'],
                                                      sbml_content=self.cleaned_data['sbml_content'], owner=owner)
        return super().save()


class CobraModelNameUpdateForm(InstanceForm):
    name = forms.CharField(max_length=200)
    desc = forms.CharField(max_length=200)
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='name')

    def save(self, model=None):
        if model:
            if not self.is_valid():
                raise ValueError()
            model.name = self.cleaned_data['name']
            model.desc = self.cleaned_data['desc']
            model.save()
            self.instance = model
        return super().save()


class CobraModelObjectiveUpdateForm(InstanceForm):
    objective = forms.CharField()
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='objective')

    def save(self, model=None):
        if model:
            if self.errors:
                raise ValueError()
            cobra_model: cobra.Model = model.build()
            cobra_model.objective = self.cleaned_data['objective']
            model.sbml_content = dump_sbml(cobra_model)
            model.save()
            self.instance = model
        return super().save()


def get_reaction_json(reaction: cobra.Reaction) -> Dict[str, Any]:
    return {
        # 'cobra_id': reaction.id,
        'name': reaction.name,
        # 'subsystem': reaction.subsystem,
        # 'lower_bound': reaction.lower_bound,
        # 'upper_bound': reaction.upper_bound,
        # 'gene_reaction_rule': reaction.gene_reaction_rule,
        # 'gene_name_reaction_rule': reaction.gene_name_reaction_rule,
        # 'metabolites_with_coefficients': dict(zip(
        #     [metabolite.id for metabolite in reaction.metabolites],
        #     reaction.get_coefficients([metabolite.id for metabolite in reaction.metabolites])
        # )),
        'metabolites': [metabolite.name for metabolite in reaction.metabolites],
        'genes': [gene.name for gene in reaction.genes],
    }


class CobraModelReactionDeleteForm(InstanceForm):
    pre_reaction_id = forms.CharField()
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='del_reaction')

    def save(self, model=None):
        if model:
            if self.errors:
                raise ValueError()
            cobra_model: cobra.Model = model.build()
            pre_reaction_id_list = self.cleaned_data['pre_reaction_id'].split(',')
            pre_reaction_info = {
                'reactions': [
                    get_reaction_json(cobra_model.reactions.get_by_id(reaction_id))
                    for reaction_id in pre_reaction_id_list
                ],
            }
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            pre_info=json.dumps(pre_reaction_info))
            cobra_model.remove_reactions(pre_reaction_id_list)
            model.sbml_content = dump_sbml(cobra_model)
            model.save()
            self.instance = model
        return super().save()


class CobraModelReactionCreateForm(InstanceForm):
    cobra_id = forms.CharField(max_length=600)
    name = forms.CharField(max_length=600)
    subsystem = forms.CharField(max_length=200)
    lower_bound = forms.FloatField(initial=0.0)
    upper_bound = forms.FloatField(initial=1000.0)
    gene_reaction_rule = forms.CharField()
    metabolites_with_coefficients = forms.CharField()
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='add_reaction')

    def save(self, model=None):
        if model:
            if self.errors:
                raise ValueError()
            cobra_model: cobra.Model = model.build()
            metabolites_with_coefficients_dict = {
                cobra_model.metabolites.get_by_id(metabolite_id): coefficient
                for metabolite_id, coefficient in
                json.loads(self.cleaned_data['metabolites_with_coefficients']).items()
            }
            cobra_reaction = cobra.Reaction(id=self.cleaned_data['cobra_id'], name=self.cleaned_data['name'],
                                            subsystem=self.cleaned_data['subsystem'],
                                            lower_bound=self.cleaned_data['lower_bound'],
                                            upper_bound=self.cleaned_data['upper_bound'])
            cobra_reaction.add_metabolites(metabolites_with_coefficients_dict)
            cobra_model.add_reactions([cobra_reaction])
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            new_info=json.dumps(get_reaction_json(cobra_reaction)))
            model.sbml_content = dump_sbml(cobra_model)
            model.save()
            self.instance = model
        return super().save()


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


class CleanDeletedGenesMixin:
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['deleted_genes'] = clean_comma_separated_str(self, cleaned_data.get('deleted_genes', ''))
        return cleaned_data


class CobraFbaForm(CleanDeletedGenesMixin, forms.ModelForm):
    class Meta:
        model = CobraFba
        fields = ['desc', 'deleted_genes']


class CobraFvaForm(CleanDeletedGenesMixin, forms.ModelForm):
    class Meta:
        model = CobraFva
        fields = ['desc', 'reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor', 'deleted_genes']

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['reaction_list'] = clean_comma_separated_str(self, cleaned_data.get('reaction_list', ''))
        return cleaned_data
