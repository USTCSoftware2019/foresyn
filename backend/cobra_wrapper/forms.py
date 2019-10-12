import json

from django import forms
import cobra

from .models import CobraModel, CobraFva, CobraModelChange
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
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='name')

    def save(self, model=None):
        if model:
            if not self.is_valid():
                raise ValueError()
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            pre_info=model.name, new_info=self.cleaned_data['name'])
            model.name = self.cleaned_data['name']
            model.save()
            self.instance = model
        return super().save()


class CobraModelSbmlContentUpdateForm(CleanSbmlContentMixin, InstanceForm):
    sbml_content = forms.FileField(required=False)
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='sbml_content')

    def save(self, model=None):
        if model:
            if self.errors:
                raise ValueError()
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model)
            model.sbml_content = self.cleaned_data['sbml_content']
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
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            new_info=self.cleaned_data['objective'])
            cobra_model: cobra.Model = model.build()
            cobra_model.objective = self.cleaned_data['objective']
            model.sbml_content = dump_sbml(cobra_model)
            model.save()
            self.instance = model
        return super().save()


class CobraModelReactionDeleteForm(InstanceForm):
    pre_reaction_id = forms.CharField()
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='del_reaction')

    def save(self, model=None):
        if model:
            if self.errors:
                raise ValueError()
            pre_reaction_id_list = self.cleaned_data['pre_reaction_id'].split(',')
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            pre_info=', '.join(pre_reaction_id_list))
            cobra_model: cobra.Model = model.build()
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
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            new_info=self.cleaned_data['cobra_id'])
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
            model.sbml_content = dump_sbml(cobra_model)
            model.save()
            self.instance = model
        return super().save()


cobra_model_update_forms = {
    'name': CobraModelNameUpdateForm,
    'sbml_content': CobraModelSbmlContentUpdateForm,
    'objective': CobraModelObjectiveUpdateForm,
    'del_reaction': CobraModelReactionDeleteForm,
    'add_reaction': CobraModelReactionCreateForm,
}


# TODO(myl7)
class CobraFvaForm(forms.ModelForm):
    class Meta:
        model = CobraFva
        fields = ['desc', 'reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor']
