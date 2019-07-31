from django import forms
from django.db import models
from django.contrib.auth.models import User

from .models import CobraMetabolite, CobraReaction, CobraModel


# def clean_pk_list(form, field, model):
#     """Convert pk list field in form to model list
#     :param form: Form to be converted. Make sure form.owner has been set to a User
#     :param field: Str. Use constexpr for this field.
#     :param model: model class searched
#     """
#     assert isinstance(form.get('owner'), User)

#     try:
#         model_list = [model.objects.get(pk=int(pk), owner=form.get('owner')) for pk in form.get(field).split()]
#     except models.ObjectDoesNotExist:
#         form.add_error(field, 'invalid pk value in pk list')
#     except ValueError:
#         form.add_error(field, 'invalid type of pk in pk list')
#     else:
#         setattr(form, field, model_list)


class CobraMetaboliteForm(forms.ModelForm):
    class Meta:
        model = CobraMetabolite
        fields = ['owner', 'cobra_id', 'name', 'formula', 'charge', 'compartment']


class CobraReactionForm(forms.ModelForm):
    class Meta:
        model = CobraReaction
        fields = [
            'owner', 'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient',
            'coefficients', 'gene_reaction_rule'
        ]

    def clean(self):
        cleaned_data = super().clean()
        metabolites = cleaned_data.get('metabolites')
        coefficients = cleaned_data.get('coefficients')

        # assert isinstance(metabolites.pop(None), (CobraMetabolite, type(None)))  # TODO:

        try:
            coefficients = [float(coefficient) for coefficient in coefficients.split()]
        except ValueError:
            self.add_error('coefficients', 'coefficients contains non-float value')
        else:
            if len(metabolites) != len(coefficients):
                self.add_error('coefficients', 'len of coefficients and metabolites are not the same')


class CobraModelForm(forms.ModelForm):
    class Meta:
        model = CobraModel
        fields = ['owner', 'cobra_id', 'name', 'objective']


class FvaForm(forms.Form):
    pass  # TODO:
