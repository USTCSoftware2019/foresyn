from django import forms
from haystack.forms import ModelSearchForm


class ModifiedModelSearchForm(ModelSearchForm):
    """
    We inherit the ModelSearchForm to make the 'q' field required
    ```required=True```

    Otherwise, when the 'q' field is blank, form.is_vaild() still return True
    """
    q = forms.CharField(required=True, label='Search',
                        widget=forms.TextInput(attrs={'type': 'search'}))
    MODEL_CHOICES = [
        ('model', 'Model'),
        ('metabolite', 'Metabolite'),
        ('reaction', 'Reaction'),
        ('gene', 'Gene')
    ]
    model = forms.ChoiceField(choices=MODEL_CHOICES, required=False)
    page = forms.IntegerField(required=False)
