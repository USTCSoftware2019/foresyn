from django import forms

from .models import CobraMetabolite, CobraReaction, CobraModel, CobraFva


class CobraReactionForm(forms.ModelForm):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metabolites'] = forms.ModelMultipleChoiceField(
            CobraMetabolite.objects.filter(owner=owner), required=False
        )

    class Meta:
        model = CobraReaction
        fields = [
            'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'metabolites', 'coefficients',
            'gene_reaction_rule'
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


class CobraFvaForm(forms.ModelForm):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reaction_list'] = forms.ModelMultipleChoiceField(
            CobraReaction.objects.filter(owner=owner), required=False
        )

    class Meta:
        model = CobraFva
        fields = ['desc', 'reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor']
