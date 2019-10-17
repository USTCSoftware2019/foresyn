from django.shortcuts import render, redirect, reverse
from django.views.generic import FormView
from haystack.generic_views import SearchMixin

from bigg_database.models import Gene as BiggGene
from bigg_database.models import Metabolite as BiggMetabolite
from bigg_database.models import Model as BiggModel
from bigg_database.models import Reaction as BiggReaction

from .forms import ModifiedModelSearchForm, BiggOptimizedSearchForm


class BaseSearchView(SearchMixin, FormView):
    form_class = ModifiedModelSearchForm
    models = None

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.models, **self.get_form_kwargs())

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.queryset = form.search()
        context = {
            self.form_name: form,
            'query': form.cleaned_data['q'],
            'object_list': self.queryset,
            'search_model': form.search_model._meta.verbose_name,
            'search_result_count': len(self.queryset)
        }
        return context


class DatabaseSearchView(BaseSearchView):
    form_class = BiggOptimizedSearchForm
    models = [BiggModel, BiggReaction, BiggMetabolite, BiggGene]
    template_name = 'bigg_database/search_result.html'
    paginate_by = 10

    def form_valid(self, form):
        context = super().form_valid(form)

        total_number = form.additional_model_count()
        context = {
            'total_count': sum(count for _, count in total_number.items()),
            'counts': total_number,
            **context
        }
        context = self.get_context_data(**context)
        return self.render_to_response(context)

    def form_invalid(self, form):
        return redirect(reverse('accounts:profile'))
