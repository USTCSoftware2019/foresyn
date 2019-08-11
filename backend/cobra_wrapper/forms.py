from django import forms

from .models import CobraMetabolite, CobraReaction, CobraModel


class CobraReactionForm(forms.ModelForm):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metabolites'] = forms.ModelMultipleChoiceField(
            CobraMetabolite.objects.filter(owner=owner), required=False
        )

    class Meta:
        model = CobraReaction
        fields = [
            'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'metabolites',
            'coefficients', 'gene_reaction_rule'
        ]

    def clean(self):
        cleaned_data = super().clean()
        coefficients = cleaned_data.get('coefficients', []).split()
        metabolites = cleaned_data.get('metabolites', [])

        if len(coefficients) != len(metabolites):
            self.add_error('coefficients', 'len of coefficients and metabolites are not the same')


class CobraModelForm(forms.ModelForm):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reactions'] = forms.ModelMultipleChoiceField(
            CobraReaction.objects.filter(owner=owner), required=False
        )

    class Meta:
        model = CobraModel
        fields = ['cobra_id', 'name', 'reactions', 'objective']


class CobraModelFvaForm(forms.Form):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reaction_list'] = forms.ModelMultipleChoiceField(CobraReaction.objects.filter(owner=owner))

    loopless = forms.BooleanField(initial=False, required=False)
    fraction_of_optimum = forms.FloatField(initial=1.0)
    pfba_factor = forms.NullBooleanField(initial=None)
