import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import View
from django.forms.models import model_to_dict
from fuzzywuzzy import fuzz

from .models import Metabolite, Model, Reaction


def fuzzy_search(query_set, request_name, request_data):
    return [
        instance
        for instance in query_set
        if fuzz.ratio(getattr(instance, request_name), request_data) >= MATCH_RATIO
    ]


def search_from_id(model, bigg_id):
    pass


def search_from_name(model, name):
    pass


class SearchView(View):
    http_method_names = ['get']
    model = None
    by = ['bigg_id', 'name']

    def get(self, request):
        empty_json = '[]'

        if self.model is None:
            raise RuntimeError("model field not specified")

        bigg_id = request.GET.get('bigg_id')
        name = request.GET.get('name')
        if bigg_id is not None and 'bigg_id' in self.by:
            return search_from_id(self.model, bigg_id)
        elif name is not None and 'name' in self.by:
            return search_from_name(self.model, name)
        else:
            return JsonResponse(empty_json)


class ModelSearchView(SearchView):
    model = Model
    by = ['bigg_id']


class MetaboliteSearchView(SearchView):
    model = Metabolite


class ReactionSearchView(SearchView):
    model = Reaction


class CustomDetailView(View):
    http_method_names = ['get']
    fields = []  # Don't include foreign key in this. Override get_context_data instead.
    model = None

    def __init__(self):
        super().__init__()
        self.context_object = None

    def get_context_data(self, pk):
        result = self.model.objects.get(pk=pk)
        self.context_object = result
        return model_to_dict(result, fields=self.fields)

    def get(self, request, pk):
        try:
            return JsonResponse(self.get_context_data(pk), status=200)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)


class ModelDetailView(CustomDetailView):
    fields = ['id', 'bigg_id', 'compartments', 'version']
    model = Model

    def get_context_data(self, pk):
        context = super().get_context_data(pk)
        context['reaction_count'] = self.context_object.reaction_set.count()
        context['metabolite_count'] = self.context_object.metabolite_set.count()


class MetaboliteDetailView(CustomDetailView):
    fields = ['id', 'bigg_id', 'name', 'formulae', 'charges', 'database_links']
    model = Metabolite

    def get_context_data(self, pk):
        context = super().get_context_data(pk)
        context['reaction_count'] = self.context_object.reactions.count()
        context['model_count'] = self.context_object.models.count()


class ReactionDetailView(CustomDetailView):
    fields = ['id', 'bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    model = Reaction

    def get_context_data(self, pk):
        context = super().get_context_data(pk)
        context['model_count'] = self.context_object.models.count()
        context['metabolite_count'] = self.context_object.metabolite_set.count()


