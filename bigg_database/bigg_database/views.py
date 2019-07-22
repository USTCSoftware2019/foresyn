import json

import django.core.exceptions
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import View
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
