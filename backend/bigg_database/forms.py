from django import forms


class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=127)

    SEARCH_MODEL_CHOICES = [
        ('model', 'Model'),
        ('metabolite', 'Metabolite'),
        ('reaction', 'Reaction'),
        ('gene', 'Gene')
    ]

    search_model = forms.ChoiceField(choices=SEARCH_MODEL_CHOICES)
