import json

from django.core.exceptions import ObjectDoesNotExist
import django.core.exceptions
from django.forms.models import model_to_dict as origin_model_to_dict
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import View
from fuzzywuzzy import fuzz

from .models import Gene, Metabolite, Model, Reaction

MATCH_RATIO = 80


def fuzzy_search(query_set, request_name, request_data):
    request_name = request_name.lower()
    request_data = request_data.lower()
    return [
        instance
        for instance in query_set
        if fuzz.partial_ratio(getattr(instance, request_name).lower(), request_data) >= MATCH_RATIO
    ]


def model_to_dict(instance, fields=None, count_number_fields=None, exclude=None):
    ret_dict = origin_model_to_dict(instance, fields=fields, exclude=exclude)
    if count_number_fields:
        ret_dict.update({
            field + '_count': getattr(instance, field).count()
            for field in count_number_fields
        })
    return ret_dict


class SearchView(View):
    http_method_names = ['get']
    model = None
    by = ['bigg_id', 'name']
    fields = None
    count_number_fields = None

    def get(self, request):
        if self.model is None or self.fields is None:
            raise RuntimeError("model or fields not specified")

        bigg_id = request.GET.get('bigg_id')
        name = request.GET.get('name')
        if bigg_id is not None and 'bigg_id' in self.by:
            return JsonResponse({'result': [
                model_to_dict(instance, fields=self.fields,
                              count_number_fields=self.count_number_fields)
                for instance in fuzzy_search(self.model.objects.all(), 'bigg_id', bigg_id)
            ]})
        elif name is not None and 'name' in self.by:
            return JsonResponse({'result': [
                model_to_dict(instance, fields=self.fields,
                              count_number_fields=self.count_number_fields)
                for instance in fuzzy_search(self.model.objects.all(), 'name', name)
            ]})
        else:
            return JsonResponse({'result': []})


class ModelSearchView(SearchView):
    model = Model
    by = ['bigg_id']
    fields = ['bigg_id', 'compartments', 'id']
    count_number_fields = ['reaction_set', 'metabolite_set', 'gene_set']


class MetaboliteSearchView(SearchView):
    model = Metabolite
    by = ['bigg_id', 'name']
    fields = ['bigg_id', 'name', 'formulae', 'charges', 'database_links', 'id']
    count_number_fields = ['reactions', 'models']


class ReactionSearchView(SearchView):
    model = Reaction
    by = ['bigg_id', 'name']
    fields = ['bigg_id', 'name', 'reaction_string',
              'pseudoreaction', 'database_links', 'id']
    count_number_fields = ['models', 'metabolite_set', 'gene_set']


class GeneSearchView(SearchView):
    model = Gene
    by = ['bigg_id', 'name']
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links', 'id']
    count_number_fields = ['reactions', 'models']


class CustomDetailView(View):
    http_method_names = ['get']
    fields = None  # Don't include foreign key in this. Override get_context_data instead.
    model = None

    def __init__(self):
        super().__init__()
        self.context_object = None

    def get_context_data(self, pk):
        result = self.model.objects.get(pk=pk)
        self.context_object = result
        return origin_model_to_dict(result, fields=self.fields)

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


class GeneDetailView(CustomDetailView):
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links', 'id']
    model = Gene

    def get_context_data(self, pk):
        context = super().get_context_data(pk)
        context['model_count'] = self.context_object.models.count()
        context['reaction_count'] = self.context_object.reactions.count()
