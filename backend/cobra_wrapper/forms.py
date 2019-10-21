import json

from django import forms
import cobra

from . import models
from .utils import dump_sbml, get_reaction_json, clean_comma_separated_str, load_comma_separated_str


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
        except Exception:
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
        model = models.CobraModel.objects.create(name=self.cleaned_data['name'], desc=self.cleaned_data['desc'],
                                                 sbml_content=self.cleaned_data['sbml_content'], owner=owner)
        model.cache(model.build())
        return model


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
        try:
            cobra_model.objective = self.cleaned_data['objective']
        except Exception:
            pass
        else:
            model.sbml_content = dump_sbml(cobra_model)
            model.save()
        return model


class CobraModelReactionDeleteForm(forms.Form):
    deleted_reaction_id = forms.CharField(min_length=1)
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='del_reaction')

    def clean(self):
        cleaned_data = super().clean()
        deleted_reaction_id = load_comma_separated_str(
            clean_comma_separated_str(self, cleaned_data.get('deleted_reaction_id', '')))
        reactions = [reaction['cobra_id'] for reaction in json.loads(self.model_object.reactions)]
        for reaction in deleted_reaction_id:
            if reaction not in reactions:
                self.add_error('deleted_reaction_id', '{} can not be found in the model'.format(reaction))
        cleaned_data['deleted_reaction_id'] = ','.join(deleted_reaction_id)
        return cleaned_data

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
        model.cache(cobra_model)
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

    # TODO(myl7): More validation
    def save(self, model):
        if self.errors:
            raise ValueError()
        cobra_model: cobra.Model = model.build()
        cobra_reaction = cobra.Reaction(id=self.cleaned_data['cobra_id'], name=self.cleaned_data['name'],
                                        subsystem=self.cleaned_data['subsystem'],
                                        lower_bound=float(self.cleaned_data['lower_bound']),
                                        upper_bound=float(self.cleaned_data['upper_bound']))
        cobra_model.add_reactions([cobra_reaction])
        cobra_reaction.reaction = self.cleaned_data['reaction_str']
        cobra_reaction.gene_reaction_rule = self.cleaned_data['gene_reaction_rule']
        models.CobraModelChange.objects.create(change_type=self.cleaned_data['change_type'], model=model,
                                               reaction_info=json.dumps({
                                                   'reactions': [get_reaction_json(cobra_reaction)],
                                               }))
        model.sbml_content = dump_sbml(cobra_model)
        model.save()
        model.cache(cobra_model)
        return model


class CobraModelReactionUpdateForm(forms.Form):
    cobra_id = forms.CharField(max_length=600, required=False)
    name = forms.CharField(max_length=600, required=False)
    subsystem = forms.CharField(max_length=200, required=False)
    lower_bound = forms.FloatField(initial=0.0, required=False)
    upper_bound = forms.FloatField(initial=1000.0, required=False)
    reaction_str = forms.CharField(required=False)
    gene_reaction_rule = forms.CharField(required=False)
    change_type = forms.CharField(widget=forms.HiddenInput(), initial='update_reaction')


cobra_model_update_forms = {
    'name': CobraModelNameUpdateForm,
    'objective': CobraModelObjectiveUpdateForm,
    'del_reaction': CobraModelReactionDeleteForm,
    'add_reaction': CobraModelReactionCreateForm,
}


class CobraModelChangeRestoreForm(forms.Form):
    name = forms.CharField(max_length=200, min_length=1)
    desc = forms.CharField(max_length=200, required=False)


class CleanDeletedGenesMixin:
    def clean(self: forms.Form):
        cleaned_data = super().clean()
        deleted_genes = load_comma_separated_str(
            clean_comma_separated_str(self, cleaned_data.get('deleted_genes', '')))
        genes = [gene['cobra_id'] for gene in json.loads(self.model_object.genes)]
        for gene in deleted_genes:
            if gene not in genes:
                self.add_error('deleted_genes', '{} can not be found in the model'.format(gene))
        cleaned_data['deleted_genes'] = ','.join(deleted_genes)
        return cleaned_data


class CobraFbaForm(CleanDeletedGenesMixin, forms.ModelForm):
    class Meta:
        model = models.CobraFba
        fields = ['desc', 'deleted_genes']


class CobraRgeFbaForm(CleanDeletedGenesMixin, forms.ModelForm):
    class Meta:
        model = models.CobraRgeFba
        fields = ['desc', 'deleted_genes']


class CobraFvaForm(CleanDeletedGenesMixin, forms.ModelForm):
    class Meta:
        model = models.CobraFva
        fields = ['desc', 'reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor', 'deleted_genes']

    def clean(self):
        cleaned_data = super().clean()
        reaction_list = load_comma_separated_str(
            clean_comma_separated_str(self, cleaned_data.get('reaction_list', '')))
        reactions = [reaction['cobra_id'] for reaction in json.loads(self.model_object.reactions)]
        for reaction in reaction_list:
            if reaction not in reactions:
                self.add_error('reaction_list', '{} can not be found in the model'.format(reaction))
        cleaned_data['reaction_list'] = ','.join(reaction_list)
        return cleaned_data
