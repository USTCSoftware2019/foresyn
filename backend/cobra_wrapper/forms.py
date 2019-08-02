import enum

from django import forms

from .models import CobraReaction


class CobraModelFvaForm(forms.Form):
    reaction_list = forms.ModelMultipleChoiceField(CobraReaction.objects.all())  # TODO: Limit choices
    loopless = forms.BooleanField(initial=False, required=False)
    fraction_of_optimum = forms.FloatField(initial=1.0)
    pfba_factor = forms.NullBooleanField(initial=None)
