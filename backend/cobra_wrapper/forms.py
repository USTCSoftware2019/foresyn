from django import forms

from .models import CobraReaction


class CobraModelFvaForm(forms.Form):
    reaction_list = forms.ModelChoiceField(CobraReaction, required=False)
    loopless = forms.BooleanField(default=False)
    fraction_of_optimum = forms.FloatField(default=1.0)
    pfba_factor = forms.NullBooleanField(default=None)
