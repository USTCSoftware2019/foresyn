from django import forms
from django.contrib.auth.models import User

from .models import CobraMetabolite, CobraReaction, CobraModel


def convert_pk_list(form, field, model):
    """Convert pk list field in form to model list
    :param form: Form to be converted. Make sure form.owner has been set to a User
    :param field: Str
    :param model: model class searched
    """
    assert isinstance(form.get('owner'), User)
    model_list = [model.objects.get(pk=pk, owner=form.get('owner')) for pk in form.get(field).split()]
    setattr(form, field, model_list)


class CobraMetaboliteForm(forms.ModelForm):
    model = CobraMetabolite
    fields = ['owner', 'cobra_id', 'name', 'formula', 'charge', 'compartment']


class CobraReactionForm(forms.ModelForm):
    models = CobraReaction
    fields = [
        'owner', 'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient',
        'coefficients', 'gene_reaction_rule'
    ]

    def clean(self):
        cleaned_data = super().clean()
        metabolites = cleaned_data.get('metabolites')
        coefficients = cleaned_data.get('coefficients')

        assert isinstance(metabolites.pop(None), (CobraMetabolite, type(None)))

        try:
            coefficients = [float(coefficient) for coefficient in coefficients.split()]
        except ValueError:
            raise forms.ValidationError('coefficients contains non-float value')

        if len(metabolites) != len(coefficients):
            raise forms.ValidationError('len of metabolites and coefficients are not the same')


class CobraModelForm(forms.Form):
    models = CobraModel
    fields = ['owner', 'cobra_id', 'name', 'objective']


class FvaForm(forms.Form):
    pass
