import enum

from django import forms

from .models import CobraReaction


class CobraModelFvaForm(forms.Form):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reaction_list'] = forms.ModelMultipleChoiceField(CobraReaction.objects.filter(owner=owner))

    loopless = forms.BooleanField(initial=False, required=False)
    fraction_of_optimum = forms.FloatField(initial=1.0)
    pfba_factor = forms.NullBooleanField(initial=None)
