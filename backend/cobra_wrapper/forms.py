import io
import json

from django import forms
import cobra

from .models import CobraModel, CobraFva, CobraModelChange


class CleanSbmlContentMixin:
    def clean(self: forms.Form):
        cleaned_data = super().clean()
        try:
            cleaned_data['sbml_content'] = cleaned_data['sbml_content'].read()
        except UnicodeDecodeError:
            self.add_error('sbml_content', 'Can not decode SBML file with utf-8')


class CobraModelCreateForm(CleanSbmlContentMixin, forms.Form):
    sbml_content = forms.FileField()
    name = forms.CharField(max_length=200)


class CobraModelNameUpdateForm(forms.Form):
    name = forms.CharField(max_length=200)
    change_type = forms.CharField(disabled=True, initial='name')

    def save(self, model):
        if self.is_valid():
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            pre_info=model.name, new_info=self.cleaned_data['name'])
            model.name = self.cleaned_data['name']
            model.save()


class CobraModelSbmlContentUpdateForm(CleanSbmlContentMixin, forms.Form):
    sbml_content = forms.FileField(required=False)
    change_type = forms.CharField(disabled=True, initial='sbml_content')

    def save(self, model):
        if self.is_valid():
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model)
            model.sbml_content = self.cleaned_data['sbml_content']
            model.save()


def update_sbml_content_field(model, cobra_model):
    sbml_file = io.StringIO()
    cobra.io.write_sbml_model(cobra_model, sbml_file)
    model.sbml_content = sbml_file.read()
    model.save()


class CobraModelObjectiveUpdateForm(forms.Form):
    objective = forms.CharField()
    change_type = forms.CharField(disabled=True, initial='objective')

    def save(self, model):
        if self.is_valid():
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            new_info=self.cleaned_data['objective'])
            cobra_model: cobra.Model = model.build()
            cobra_model.objective = self.cleaned_data['objective']
            update_sbml_content_field(model, cobra_model)


class CobraModelReactionDeleteForm(forms.Form):
    pre_reaction_id = forms.CharField()

    def save(self, model):
        if self.is_valid():
            pre_reaction_id_list = self.cleaned_data['pre_reaction_id'].split(',')
            CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                            pre_info=', '.join(pre_reaction_id_list))
            cobra_model: cobra.Model = model.build()
            cobra_model.remove_reactions(pre_reaction_id_list)
            update_sbml_content_field(model, cobra_model)


class CobraModelReactionCreateForm(forms.Form):
    cobra_id = forms.CharField(max_length=600)
    name = forms.CharField(max_length=600)
    subsystem = forms.CharField(max_length=200)
    lower_bound = forms.FloatField(initial=0.0)
    upper_bound = forms.FloatField(initial=1000.0)
    gene_reaction_rule = forms.CharField()
    metabolites_with_coefficients = forms.CharField()
    change_type = forms.CharField(disabled=True, initial='add_reaction')

    def save(self, model):
        if self.is_valid():
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
            update_sbml_content_field(model, cobra_model)


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
