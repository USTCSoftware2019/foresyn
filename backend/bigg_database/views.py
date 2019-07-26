import json

import django.core.exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, reverse
from django.utils.translation import gettext as _
from django.views.generic import ListView, View
from fuzzywuzzy import fuzz

from .common import TopKHeap
from .forms import SearchForm
from .models import (Gene, Metabolite, Model, ModelMetabolite, ModelReaction,
                     Reaction, ReactionGene, ReactionMetabolite)


def fuzzy_search(query_set, request_name, request_data):
    request_name = request_name.lower()
    request_data = request_data.lower()
    t = TopKHeap(10)
    for instance in query_set:
        t.push((fuzz.partial_ratio(getattr(instance, request_name).lower(), request_data), instance))
    return t.top_k()


class SearchView(ListView):
    http_method_names = ['get', 'post']
    by = ['bigg_id', 'name']
    fields = []
    count_number_fields = []
    search_model = None

    template_name = 'bigg_database/search_result.html'
    context_object_name = 'result_list'

    def get_default_form(self):
        form = SearchForm()
        form.fields['search_by'].choices = [
            (x, x)
            for x in self.by
        ]
        return form

    def get(self, request):
        return render(request, 'bigg_database/search.html',
                      {'form': self.get_default_form()})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        for ins in self.object_list:
            for f in self.count_number_fields:
                setattr(ins, f.replace('_set', '') + '_count', getattr(ins, f).count())
        context['display_fields'] = self.fields
        context['search_key_word'] = self.form.cleaned_data['keyword']
        return context

    def get_queryset(self, *args, **kwargs):
        return fuzzy_search(
            self.search_model.objects.all(),
            self.form.get_search_by_display(),
            self.form.cleaned_data['keyword'])

    def post(self, request, *args, **kwargs):
        self.form = SearchForm(request.POST)
        self.form.fields['search_by'].choices = [
            (x, x)
            for x in self.by
        ]
        if self.form.is_valid():
            return super().get(request, *args, **kwargs)
        else:
            return render(request, 'bigg_database/search.html',
                          {
                              'form': self.get_default_form(),
                              'errors': 'Keyword or search_type is invaild'
                          })


class ModelSearchView(SearchView):
    search_model = Model
    by = ['bigg_id']
    fields = ['bigg_id', 'compartments']
    count_number_fields = ['reaction_set', 'metabolite_set', 'gene_set']


class MetaboliteSearchView(SearchView):
    search_model = Metabolite
    by = ['bigg_id', 'name']
    fields = ['bigg_id', 'name', 'formulae', 'charges']
    count_number_fields = ['reactions', 'models']


class ReactionSearchView(SearchView):
    search_model = Reaction
    by = ['bigg_id', 'name']
    fields = ['bigg_id', 'name', 'reaction_string',
              'pseudoreaction']
    count_number_fields = ['models', 'metabolite_set', 'gene_set']


class GeneSearchView(SearchView):
    search_model = Gene
    by = ['bigg_id', 'name']
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string']
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
        return context


class MetaboliteDetailView(CustomDetailView):
    fields = ['id', 'bigg_id', 'name', 'formulae', 'charges', 'database_links']
    model = Metabolite

    def get_context_data(self, pk):
        context = super().get_context_data(pk)
        context['reaction_count'] = self.context_object.reactions.count()
        context['model_count'] = self.context_object.models.count()
        return context


class ReactionDetailView(CustomDetailView):
    fields = ['id', 'bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    model = Reaction

    def get_context_data(self, pk):
        context = super().get_context_data(pk)
        context['model_count'] = self.context_object.models.count()
        context['metabolite_count'] = self.context_object.metabolite_set.count()
        return context


class GeneDetailView(CustomDetailView):
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links', 'id', 'bigg_id', 'name']
    model = Gene

    def get_context_data(self, pk):
        context = super().get_context_data(pk)
        context['model_count'] = self.context_object.models.count()
        context['reaction_count'] = self.context_object.reactions.count()
        return context


class CustomListView(View):
    '''
    A custom ListView

    This ListView returns json data, in format: {'result': ```list_data```}
    The class inheriting it needs to overwrite 'fields', 'from_model' and
    'to_model' to make it work correctly.

    As for 'from_model' and 'to_model', this parent class will implement
    ```getattr(self.from_model.objects.get(id=pk), self.to_model).all()``` to
    get the list to be returned.

    So, be careful about whether to add '_set' as the suffix to the 'to_model'
    variable
    '''
    fields = None
    from_model = None
    to_model = None

    def get_context_data(self, instance, fields):
        return model_to_dict(instance, fields=fields)

    def get_query_set(self):
        # In order to reuse this view in 'reverse lookup' views,
        # delete the '_set'. To use 'forward lookup' views, please
        # add '_set' as suffix to their to_model variables.
        # Instead, it is not necessary to add '_set' to their to_model
        # variables when using 'reverse lookup' views
        return getattr(self.from_model_instance, self.to_model).all()

    def __init__(self):
        if not self.fields or not self.from_model or not self.to_model:
            raise RuntimeError('"fileds" and "from_model" needs to be set')

    def get(self, request, pk):
        try:
            self.from_model_instance = self.from_model.objects.get(id=pk)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        return JsonResponse({
            'result': [
                self.get_context_data(instance, fields=self.fields)
                for instance in self.get_query_set()
            ]
        })


class GenesInModel(CustomListView):
    '''
    Lookup which genes are related to a model
    '''
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links', 'id']
    from_model = Model
    to_model = 'gene_set'


class MetabolitesInModel(CustomListView):
    '''
    Lookup which metabolites are in a model
    '''
    fields = ['id', 'bigg_id', 'name', 'formulae', 'charges', 'database_links']
    from_model = Model
    to_model = 'metabolite_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mm = ModelMetabolite.objects.get(model=self.from_model_instance, metabolite=instance)
        context['organism'] = mm.organism
        return context


class ReactionsInModel(CustomListView):
    '''
    Lookup which reactions are in a model
    '''
    fields = ['id', 'bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    from_model = Model
    to_model = 'reaction_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mr = ModelReaction.objects.get(model=self.from_model_instance, reaction=instance)
        context['organism'] = mr.organism
        context['lower_bound'] = mr.lower_bound
        context['upper_bound'] = mr.upper_bound
        context['subsystem'] = mr.subsystem
        context['gene_reaction_rule'] = mr.gene_reaction_rule
        return context


class MetabolitesInReaction(CustomListView):
    '''
    Lookup which metabolites are in a reaction
    '''
    fields = ['id', 'bigg_id', 'name', 'formulae', 'charges', 'database_links']
    from_model = Reaction
    to_model = 'metabolite_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rm = ReactionMetabolite.objects.get(metabolite=instance, reaction=self.from_model_instance)
        context['stoichiometry'] = rm.stoichiometry
        return context


class GenesInReaction(CustomListView):
    '''
    Lookup which genes are related to reaction
    '''
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links', 'id', 'bigg_id', 'name']
    from_model = Reaction
    to_model = 'gene_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rg = ReactionGene.objects.get(gene=instance, reaction=self.from_model_instance)
        context['gene_reaction_rule'] = rg.gene_reaction_rule

        return context


class GeneFromModels(CustomListView):
    '''
    Reverse lookup which models contain a certain gene
    '''
    fields = ['bigg_id', 'compartments', 'id']
    from_model = Gene
    to_model = 'models'


class MetaboliteFromModels(CustomListView):
    '''
    Reverse lookup which models contain a certain metabolite
    '''
    fields = ['bigg_id', 'compartments', 'id']
    from_model = Metabolite
    to_model = 'models'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mm = ModelMetabolite.objects.get(model=instance, metabolite=self.from_model_instance)
        context['organism'] = mm.organism
        return context


class ReactionFromModels(CustomListView):
    '''
    Reverse lookup which models contain a certain reaction
    '''
    fields = ['bigg_id', 'compartments', 'id']
    from_model = Reaction
    to_model = 'models'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mr = ModelReaction.objects.get(model=instance, reaction=self.from_model_instance)
        context['organism'] = mr.organism
        context['lower_bound'] = mr.lower_bound
        context['upper_bound'] = mr.upper_bound
        context['subsystem'] = mr.subsystem
        context['gene_reaction_rule'] = mr.gene_reaction_rule
        return context


class GeneFromReactions(CustomListView):
    '''
    Reverse lookup which reactions contain a certain gene
    '''
    fields = ['id', 'bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    from_model = Gene
    to_model = 'reactions'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rg = ReactionGene.objects.get(gene=self.from_model_instance, reaction=instance)
        context['gene_reaction_rule'] = rg.gene_reaction_rule

        return context


class MetaboliteFromReactions(CustomListView):
    '''
    Reverse lookup which reactions contain a certain metabolite
    '''
    fields = ['id', 'bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    from_model = Metabolite
    to_model = 'reactions'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rm = ReactionMetabolite.objects.get(metabolite=self.from_model_instance, reaction=instance)
        context['stoichiometry'] = rm.stoichiometry
        return context
