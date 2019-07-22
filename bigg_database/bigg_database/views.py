import json

import django.core.exceptions
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import View
from fuzzywuzzy import fuzz

from .models import Gene, Metabolite, Model, Reaction

MATCH_RATIO = 80


def fuzzy_search(query_set, request_name, request_data):
    request_name = request_name.lower()
    return [
        instance
        for instance in query_set
        if fuzz.ratio(getattr(instance, request_name).lower(), request_data) >= MATCH_RATIO
    ]


def search_from_id(model, bigg_id, fields):
    fuzzy_search_result = fuzzy_search(model.objects.all(), 'bigg_id', bigg_id)
    return [
        model_to_dict(instance, fields=fields)
        for instance in fuzzy_search_result
    ]


def search_from_name(model, name, fields):
    fuzzy_search_result = fuzzy_search(model.objects.all(), 'name', name)
    return [
        model_to_dict(instance, fields=fields)
        for instance in fuzzy_search_result
    ]


class SearchView(View):
    http_method_names = ['get']
    model = None
    by = ['bigg_id', 'name']
    fields = None

    def get(self, request):
        if self.model is None or self.fields is None:
            raise RuntimeError("model or fields not specified")

        bigg_id = request.GET.get('bigg_id')
        name = request.GET.get('name')
        if bigg_id is not None and 'bigg_id' in self.by:
            return JsonResponse({'result': search_from_id(self.model, bigg_id, self.fields)})
        elif name is not None and 'name' in self.by:
            return JsonResponse({'result': search_from_name(self.model, name, self.fields)})
        else:
            return JsonResponse({'result': []})


class ModelSearchView(SearchView):
    model = Model
    by = ['bigg_id']
    fields = ['bigg_id', 'compartments', 'pk']


class MetaboliteSearchView(SearchView):
    model = Metabolite
    by = ['bigg_id', 'name']
    fields = ['bigg_id', 'name', 'formulae', 'charges', 'database_links', 'pk']


class ReactionSearchView(SearchView):
    model = Reaction
    by = ['bigg_id', 'name']
    fields = ['bigg_id', 'name', 'reaction_string',
              'pseudoreaction', 'database_links', 'pk']


class GeneSearchView(SearchView):
    model = Gene
    by = ['bigg_id', 'name']
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links', 'pk']
