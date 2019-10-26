from django import forms


class BareSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    MODEL_CHOICES = [
        ('model', 'Model'),
        ('reaction', 'Reaction'),
        ('metabolite', 'Metabolite'),
        ('gene', 'Gene')
    ]
    model = forms.ChoiceField(choices=MODEL_CHOICES, required=False)
