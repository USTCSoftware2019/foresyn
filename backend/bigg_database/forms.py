from django import forms
from haystack.forms import ModelSearchForm
from .models import Model, Reaction, Metabolite, Gene
from haystack.query import SQ


model_map = {
    'model': Model,
    'reaction': Reaction,
    'metabolite': Metabolite,
    'gene': Gene
}


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

    default_model = 'model'

    def get_models(self):
        search_models = ['bigg_database.Reaction',
                         'bigg_database.Model',
                         'bigg_database.Metabolite',
                         'bigg_database.Gene']

        return search_models

    @property
    def model_to_search(self):
        try:
            model_name = self.cleaned_data.get('model') or self.default_model
        except AttributeError:
            model_name = self.default_model

        return model_map[model_name]

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        return self._search_model()

    def _search_model(self, model=None):
        keyword = self.cleaned_data['q']
        if model is None:
            model = self.model_to_search

        return self.searchqueryset \
            .models(model) \
            .filter(SQ(content__fuzzy=keyword)) \
            .order_by('-_score')

    def search_count(self):
        model_to_search = self.model_to_search

        if not self.is_valid():
            total_number = {
                '{}_count'.format(model_name): 0
                for model_name, model in model_map
                if model != model_to_search
            }
        else:
            total_number = {
                '{}_count'.format(model_name): len(self._search_model(model))
                for model_name, model in model_map.items()
                if model != model_to_search
            }
        return total_number





