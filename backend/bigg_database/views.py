import json
from functools import reduce
import heapq

import django.core.exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import Http404, render, reverse
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView, View
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


class ModelSearchInfo:
    search_model = Model
    by = ['bigg_id']
    view_name = 'model_detail'


class MetaboliteSearchInfo:
    search_model = Metabolite
    by = ['bigg_id', 'name']
    view_name = 'metabolite_detail'


class ReactionSearchInfo:
    search_model = Reaction
    by = ['bigg_id', 'name']
    view_name = 'reaction_detail'


class GeneSearchInfo:
    search_model = Gene
    by = ['bigg_id', 'name']
    view_name = 'gene_detail'


class SearchView(ListView):
    """
    The view to search model, reaction, gene and metabolite
    """
    http_method_names = ['get']

    template_name = 'bigg_database/search_result.html'
    context_object_name = 'result_list'

    model_info_dict = {
        'model': ModelSearchInfo,
        'reaction': ReactionSearchInfo,
        'metabolite': MetaboliteSearchInfo,
        'gene': GeneSearchInfo,
    }

    def __init__(self):
        super().__init__()
        self.form = None
        self.result_info_model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.form.cleaned_data['search_model']
        context['view_name'] = self.result_info_model.view_name
        context['search_key_word'] = self.form.cleaned_data['keyword']
        return context

    def get_queryset(self, *args, **kwargs):
        # consider using OrderedDict while your python version doesn't guarantee the order of dict
        return dict.fromkeys([element[2] for element in reduce(lambda a, b: heapq.merge(a, b, reverse=True), [
            fuzzy_search(self.model.objects.all(), search_by, self.form.cleaned_data['keyword'])
            for search_by in self.result_info_model.by
        ])])

    def get(self, request, *args, **kwargs):
        self.form = SearchForm(request.GET)
        if self.form.is_valid():
            self.result_info_model = self.model_info_dict[self.form.cleaned_data['search_model']]
            self.model = self.result_info_model.search_model
            return super().get(request, *args, **kwargs)
        else:
            return render(request, 'bigg_database/search.html', {
                'form': SearchForm()
            })


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


class RelationshipLookupView(ListView):
    '''
    This view aims to be the base view of (*)In(*)View

    The class inheriting it needs to overwrite 'from_model' and
    'to_model' to make it work correctly.

    As for 'from_model' and 'to_model', this parent class will implement
    ```getattr(self.from_model.objects.get(id=pk), self.to_model).all()``` to
    get the list to be returned.

    So, be careful about whether to add '_set' as the suffix to the 'to_model'
    variable
    '''
    http_method_names = ['get']
    from_model = None
    to_model_name = None
    template_name = 'bigg_database/relationship_lookup_list.html'
    context_object_name = 'result_list'

    def get_object_extra_info(self, instance):
        return {}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        for ins in context['result_list']:
            for key, value in self.get_object_extra_info(ins).items():
                setattr(ins, key, value)

        context['to_model_name'] = self.to_model_name.replace('_set', '')
        context['from_model'] = self.object
        context['from_model_name'] = self.from_model._meta.verbose_name

        return context

    def get_queryset(self):
        # In order to reuse this view in 'reverse lookup' views,
        # delete the '_set'. To use 'forward lookup' views, please
        # add '_set' as suffix to their to_model_name variables.
        # Instead, it is not necessary to add '_set' to their to_model_name
        # variables when using 'reverse lookup' views
        return getattr(self.object, self.to_model_name).all()

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.from_model.objects.get(id=kwargs.get('pk'))
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.from_model._meta.verbose_name})
        return super().get(self, request, *args, **kwargs)


class GenesInModel(RelationshipLookupView):
    '''
    Lookup which genes are related to a model
    '''
    from_model = Model
    to_model_name = 'gene_set'


class MetabolitesInModel(RelationshipLookupView):
    '''
    Lookup which metabolites are in a model
    '''
    from_model = Model
    to_model_name = 'metabolite_set'

    def get_object_extra_info(self, instance):
        mm = ModelMetabolite.objects.get(model=self.object, metabolite=instance)

        extra_info = {
            'organism': mm.organism,
        }
        return extra_info


class ReactionsInModel(RelationshipLookupView):
    '''
    Lookup which reactions are in a model
    '''
    from_model = Model
    to_model_name = 'reaction_set'

    def get_object_extra_info(self, instance):
        mr = ModelReaction.objects.get(model=self.object, reaction=instance)
        extra_info = {
            'organism': mr.organism,
            'lower_bound': mr.lower_bound,
            'upper_bound': mr.upper_bound,
            'subsystem': mr.subsystem,
            'gene_reaction_rule': mr.gene_reaction_rule,
        }
        return extra_info


class MetabolitesInReaction(RelationshipLookupView):
    '''
    Lookup which metabolites are in a reaction
    '''
    from_model = Reaction
    to_model_name = 'metabolite_set'

    def get_object_extra_info(self, instance):
        rm = ReactionMetabolite.objects.get(metabolite=instance, reaction=self.object)
        extra_info = {
            'stoichiometry': rm.stoichiometry
        }
        return extra_info


class GenesInReaction(RelationshipLookupView):
    '''
    Lookup which genes are related to reaction
    '''
    from_model = Reaction
    to_model_name = 'gene_set'

    def get_object_extra_info(self, instance):
        rg = ReactionGene.objects.get(gene=instance, reaction=self.object)
        extra_info = {
            'gene_reaction_rule': rg.gene_reaction_rule
        }
        return extra_info


class GeneFromModels(RelationshipLookupView):
    '''
    Reverse lookup which models contain a certain gene
    '''
    from_model = Gene
    to_model_name = 'models'
    template_name = 'bigg_database/relationship_reverse_lookup_list.html'


class MetaboliteFromModels(RelationshipLookupView):
    '''
    Reverse lookup which models contain a certain metabolite
    '''
    from_model = Metabolite
    to_model_name = 'models'
    template_name = 'bigg_database/relationship_reverse_lookup_list.html'

    def get_object_extra_info(self, instance):
        mm = ModelMetabolite.objects.get(model=instance, metabolite=self.object)
        extra_info = {
            'organism': mm.organism
        }
        return extra_info


class ReactionFromModels(RelationshipLookupView):
    '''
    Reverse lookup which models contain a certain reaction
    '''
    from_model = Reaction
    to_model_name = 'models'
    template_name = 'bigg_database/relationship_reverse_lookup_list.html'

    def get_object_extra_info(self, instance):
        mr = ModelReaction.objects.get(model=instance, reaction=self.object)
        extra_info = {
            'organism': mr.organism,
            'lower_bound': mr.lower_bound,
            'upper_bound': mr.upper_bound,
            'subsystem': mr.subsystem,
            'gene_reaction_rule': mr.gene_reaction_rule,
        }
        return extra_info


class GeneFromReactions(RelationshipLookupView):
    '''
    Reverse lookup which reactions contain a certain gene
    '''
    from_model = Gene
    to_model_name = 'reactions'
    template_name = 'bigg_database/relationship_reverse_lookup_list.html'

    def get_object_extra_info(self, instance):
        rg = ReactionGene.objects.get(gene=self.object, reaction=instance)
        extra_info = {
            'gene_reaction_rule': rg.gene_reaction_rule
        }
        return extra_info


class MetaboliteFromReactions(RelationshipLookupView):
    '''
    Reverse lookup which reactions contain a certain metabolite
    '''
    fields = ['bigg_id', 'name', 'reaction_string', 'pseudoreaction', 'database_links']
    from_model = Metabolite
    to_model_name = 'reactions'
    template_name = 'bigg_database/relationship_reverse_lookup_list.html'

    def get_object_extra_info(self, instance):
        rm = ReactionMetabolite.objects.get(metabolite=self.object, reaction=instance)
        extra_info = {
            'stoichiometry': rm.stoichiometry
        }
        return extra_info


# TODO
# Add link to from_model
class RelationshipDetailView(View):
    http_method_names = ['get']
    from_model = None
    to_model = None
    template_name = None

    def get_object_extra_info(self, *args, **kwargs):
        return {}

    def get_extra_fields(self):
        return []

    def get(self, request, *args, **kwargs):
        try:
            self.from_model_instance = self.from_model.objects.get(id=kwargs.get('from_model_pk'))
            self.to_model_instance = self.to_model.objects.get(id=kwargs.get('to_model_pk'))
        except ObjectDoesNotExist:
            raise Http404('The required from_model or to_model does not exist')

        for key, value in self.get_object_extra_info().items():
            setattr(self.to_model_instance, key, value)

        context = {
            'from_model': self.from_model_instance,
            'to_model': self.to_model_instance,
        }

        return render(request, self.template_name, context=context)


class ModelMetaboliteRelationshipDetailView(RelationshipDetailView):
    from_model = Model
    to_model = Metabolite
    template_name = 'bigg_database/model_metabolite_detail.html'

    def get_object_extra_info(self, *args, **kwargs):
        mm = ModelMetabolite.objects.get(model=self.from_model_instance,
                                         metabolite=self.to_model_instance)
        extra_info = {
            'organism': mm.organism
        }
        return extra_info


class ModelReactionRelationshipDetailView(RelationshipDetailView):
    from_model = Model
    to_model = Reaction
    template_name = 'bigg_database/model_reaction_detail.html'

    def get_object_extra_info(self, *args, **kwargs):
        mr = ModelReaction.objects.get(model=self.from_model_instance,
                                       reaction=self.to_model_instance)
        extra_info = {
            'organism': mr.organism,
            'lower_bound': mr.lower_bound,
            'upper_bound': mr.upper_bound,
            'subsystem': mr.subsystem,
            'gene_reaction_rule': mr.gene_reaction_rule,
        }
        return extra_info


class ReactionMetaboliteRelationshipDetailView(RelationshipDetailView):
    from_model = Reaction
    to_model = Metabolite
    template_name = 'bigg_database/reaction_metabolite_detail.html'

    def get_object_extra_info(self, *args, **kwargs):
        rm = ReactionMetabolite.objects.get(reaction=self.from_model_instance,
                                            metabolite=self.to_model_instance)
        extra_info = {
            'stoichiometry': rm.stoichiometry
        }
        return extra_info


class ReactionGeneRelationshipDetailView(RelationshipDetailView):
    from_model = Reaction
    to_model = Gene
    template_name = 'bigg_database/reaction_gene_detail.html'

    def get_object_extra_info(self, *args, **kwargs):
        rg = ReactionGene.objects.get(reaction=self.from_model_instance,
                                      gene=self.to_model_instance)
        extra_info = {
            'gene_reaction_rule': rg.gene_reaction_rule
        }
        return extra_info


class ModelGeneRelationshipDetailView(RelationshipDetailView):
    from_model = Model
    to_model = Gene
    template_name = 'bigg_database/model_gene_detail.html'
