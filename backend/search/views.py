from django.shortcuts import redirect, render, reverse
from django.views.generic import FormView, View
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from .forms import BareSearchForm
from .psql import Gene as psqlGene
from .psql import Metabolite as psqlMetabolite
from .psql import Model as psqlModel
from .psql import Reaction as psqlReaction
from .psql import count_search_result as psql_count_search_result
from .psql import search as psql_search


class BiGGDatabaseSearchView(MultipleObjectMixin, FormView):
    form_class = BareSearchForm
    template_name = 'bigg_database/search_result.html'
    paginate_by = 10
    model_map = {
        'model': psqlModel,
        'reaction': psqlReaction,
        'metabolite': psqlMetabolite,
        'gene': psqlGene
    }

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        q = form.cleaned_data['q']
        search_model = form.cleaned_data.get('model') or 'model'
        model = self.model_map[search_model]
        object_list = psql_search(q, model, 0.2, 0.3)

        total_number = {
            model_name: psql_count_search_result(q, model_cls)
            for model_name, model_cls in self.model_map.items()
            if model_cls != model
        }
        total_number[search_model] = object_list.count()

        context = {
            'form': form,
            'query': form.cleaned_data['q'],
            'object_list': object_list,
            'search_model': search_model,
            'search_result_count': object_list.count(),
            'total_count': sum([c for _, c in total_number.items()]),
            'counts': total_number
        }

        context = self.get_context_data(**context)
        return self.render_to_response(context)

    def form_invalid(self, form):
        return redirect(reverse('accounts:profile'))
