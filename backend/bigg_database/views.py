import json

import django.core.exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, reverse
from django.utils.translation import gettext as _
from django.views.generic import ListView, View, DetailView
from django.views.generic.detail import SingleObjectMixin
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

# TODO
# Maybe it is not suitable to display the result in this way
# Redirect to a truly list view is better
# Or submit the keyword and search_by through url param
#
# Add link to each result


class SearchView(ListView):
    '''
    the base view for ModelSearchView, MetaboliteSearchView, ReactionSearchView and GeneSearchView
    '''
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


class ModelDetailView(DetailView):
    model = Model
    context_object_name = 'model'


class MetaboliteDetailView(DetailView):
    model = Metabolite
    context_object_name = 'meta'


class ReactionDetailView(DetailView):
    model = Reaction
    context_object_name = 'reaction'


class GeneDetailView(DetailView):
    model = Gene
    context_object_name = 'gene'

# TODO
# Add link for each related object


class RelationshipLookupView(SingleObjectMixin, ListView):
    '''
    This view aims to be the base view of (*)In(*)View or (*)From(*)View

    The class inheriting it needs to overwrite 'fields', 'from_model' and
    'to_model' to make it work correctly.

    As for 'from_model' and 'to_model', this parent class will implement
    ```getattr(self.from_model.objects.get(id=pk), self.to_model).all()``` to
    get the list to be returned.

    So, be careful about whether to add '_set' as the suffix to the 'to_model'
    variable
    '''
    http_method_names = ['get', 'post']
    fields = []
    from_model = None
    to_model_name = None
    template_name = 'bigg_database/relationship_lookup_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            context['from_model'] = self.objects.name
        except AttributeError:
            context['from_model'] = self.objects.bigg_id
        context['to_model'] = self.to_model_name.replace('_set', '')
        context['display_fields'] = self.fields
        return context

    def get_query_set(self):
        # In order to reuse this view in 'reverse lookup' views,
        # delete the '_set'. To use 'forward lookup' views, please
        # add '_set' as suffix to their to_model_name variables.
        # Instead, it is not necessary to add '_set' to their to_model_name
        # variables when using 'reverse lookup' views
        return getattr(self.objects, self.to_model_name).all()

    def get(self, request, *args, **kwargs):
        self.objects = self.get_object(self.from_model.objects.all())
        return super().get(self, request, *args, **kwargs)


class GenesInModel(RelationshipLookupView):
    '''
    Lookup which genes are related to a model
    '''
    fields = ['rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links']
    from_model = Model
    to_model_name = 'gene_set'


class MetabolitesInModel(RelationshipLookupView):
    '''
    Lookup which metabolites are in a model
    '''
    fields = ['bigg_id', 'name', 'formulae', 'charges', 'database_links']
    from_model = Model
    to_model_name = 'metabolite_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mm = ModelMetabolite.objects.get(model=self.object_list, metabolite=instance)
        context['organism'] = mm.organism
        return context


class ReactionsInModel(RelationshipLookupView):
    '''
    Lookup which reactions are in a model
    '''
    fields = ['bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    from_model = Model
    to_model_name = 'reaction_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mr = ModelReaction.objects.get(model=self.object_list, reaction=instance)
        context['organism'] = mr.organism
        context['lower_bound'] = mr.lower_bound
        context['upper_bound'] = mr.upper_bound
        context['subsystem'] = mr.subsystem
        context['gene_reaction_rule'] = mr.gene_reaction_rule
        return context


class MetabolitesInReaction(RelationshipLookupView):
    '''
    Lookup which metabolites are in a reaction
    '''
    fields = ['bigg_id', 'name', 'formulae', 'charges', 'database_links']
    from_model = Reaction
    to_model_name = 'metabolite_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rm = ReactionMetabolite.objects.get(metabolite=instance, reaction=self.object_list)
        context['stoichiometry'] = rm.stoichiometry
        return context


class GenesInReaction(RelationshipLookupView):
    '''
    Lookup which genes are related to reaction
    '''
    fields = ['bigg_id', 'name', 'rightpos', 'leftpos', 'chromosome_ncbi_accession',
              'mapped_to_genbank', 'strand', 'protein_sequence',
              'dna_sequence', 'genome_name', 'genome_ref_string',
              'database_links']
    from_model = Reaction
    to_model_name = 'gene_set'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rg = ReactionGene.objects.get(gene=instance, reaction=self.object_list)
        context['gene_reaction_rule'] = rg.gene_reaction_rule

        return context


class GeneFromModels(RelationshipLookupView):
    '''
    Reverse lookup which models contain a certain gene
    '''
    fields = ['bigg_id', 'compartments']
    from_model = Gene
    to_model_name = 'models'


class MetaboliteFromModels(RelationshipLookupView):
    '''
    Reverse lookup which models contain a certain metabolite
    '''
    fields = ['bigg_id', 'compartments']
    from_model = Metabolite
    to_model_name = 'models'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mm = ModelMetabolite.objects.get(model=instance, metabolite=self.object_list)
        context['organism'] = mm.organism
        return context


class ReactionFromModels(RelationshipLookupView):
    '''
    Reverse lookup which models contain a certain reaction
    '''
    fields = ['bigg_id', 'compartments']
    from_model = Reaction
    to_model_name = 'models'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        mr = ModelReaction.objects.get(model=instance, reaction=self.object_list)
        context['organism'] = mr.organism
        context['lower_bound'] = mr.lower_bound
        context['upper_bound'] = mr.upper_bound
        context['subsystem'] = mr.subsystem
        context['gene_reaction_rule'] = mr.gene_reaction_rule
        return context


class GeneFromReactions(RelationshipLookupView):
    '''
    Reverse lookup which reactions contain a certain gene
    '''
    fields = ['bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    from_model = Gene
    to_model_name = 'reactions'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rg = ReactionGene.objects.get(gene=self.object_list, reaction=instance)
        context['gene_reaction_rule'] = rg.gene_reaction_rule

        return context


class MetaboliteFromReactions(RelationshipLookupView):
    '''
    Reverse lookup which reactions contain a certain metabolite
    '''
    fields = ['bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    from_model = Metabolite
    to_model_name = 'reactions'

    def get_context_data(self, instance, fields):
        context = super().get_context_data(instance, fields)
        rm = ReactionMetabolite.objects.get(metabolite=self.object_list, reaction=instance)
        context['stoichiometry'] = rm.stoichiometry
        return context
