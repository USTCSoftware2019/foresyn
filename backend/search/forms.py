from django import forms
from haystack.forms import ModelSearchForm
from haystack.query import SQ
from django.apps import apps


class ModifiedModelSearchForm(ModelSearchForm):
    q = forms.CharField(required=True, label='Search',
                        widget=forms.TextInput(attrs={'type': 'search'}))

    '''
    This should be an class, not str
    '''
    default_model = None

    def __init__(self, models, *args, **kwargs):
        """
        The first model in models will be the default model to search if default_model undefined
        """
        super().__init__(*args, **kwargs)

        '''
        Create model field, describes which model to search
        '''
        if not models:
            raise ValueError("Models to search must be specified")

        self.fields['model'] = forms.ChoiceField(required=False,
                                                 choices=[
                                                     (o._meta.label, o._meta.verbose_name)
                                                     for o in models
                                                 ])

        '''
        This will create something like
        ```
        ['bigg_database.Reaction',
        'bigg_database.Model',
        'bigg_database.Metabolite',
        'bigg_database.Gene']
        ```
        '''
        self.models = models
        self.models_str = [
            o._meta.label
            for o in models
        ]
        self.queryset = None

    @property
    def search_model(self):
        query_model = None
        if self.cleaned_data.get('model'):
            query_model = apps.get_model(self.cleaned_data.get('model'))

        return query_model or self.default_model or self.models[0]

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        self.queryset = self._search_model()
        return self.queryset

    def _search_model(self, model=None):
        keyword = self.cleaned_data['q']

        model = model or self.search_model

        return self.searchqueryset \
            .models(model) \
            .filter(SQ(content__fuzzy=keyword)) \
            .order_by('-_score')

    def additional_model_count(self):
        if not self.is_valid():
            total_number = {
                model._meta.verbose_name: 0
                for model in self.models
            }
        else:
            total_number = {
                model._meta.verbose_name: len(self._search_model(model))
                for model in self.models
                if model != self.search_model
            }

        if self.queryset is not None:
            this_cnt = self.queryset.count()
        else:
            this_cnt = self.search().count()

        total_number[self.search_model._meta.verbose_name] = this_cnt

        return total_number