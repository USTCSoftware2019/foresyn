from django.views import View

from cobra_wrapper.models import CobraModel, CobraMetabolite, CobraReaction
from bigg_database.models import Model as DataModel, Metabolite as DataMetabolite, Reaction as DataReaction
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .common import reaction_string_to_metabolites, data_metabolite_to_cobra_metabolite


class AddDataModelToCobra(View):
    def post(self, request, database_pk):
        datamodel_object = DataModel.objects.get(pk=database_pk)
        cobramodel_object = CobraModel()
        # relationship
        cobramodel_object.identifier = datamodel_object.bigg_id
        cobramodel_object.name = datamodel_object.bigg_id

        datamodel_reactions = datamodel_object.modelreaction_set
        for datareaction in datamodel_reactions.all():
            # waiting for test data...
            # TBD
            pass

        return JsonResponse("test")


class AddDataReactionToCobra(View):
    def post(self, request, database_pk):
        try:
            data_reaction_object = DataReaction.objects.get(pk=database_pk)
        except ObjectDoesNotExist:
            return JsonResponse("error")

        cobra_reaction_object = CobraReaction()

        # Add metabolites first
        reaction_string = data_reaction_object.reaction_string
        (metabolite_names, coefficients) = reaction_string_to_metabolites(reaction_string)
        for name in metabolite_names:
            cobra_metabolite_object = data_metabolite_to_cobra_metabolite("bigg_id", name)
            cobra_reaction_object.save()
            cobra_reaction_object.metabolites.add(cobra_metabolite_object)

        # relationship
        cobra_reaction_object.name = data_reaction_object.name
        cobra_reaction_object.identifier = data_reaction_object.bigg_id
        # cobra_reaction_object.subsystem
        # cobra_reaction_object.upper_bound
        # cobra_reaction_object.lower_bound
        # cobra_reaction_object.objective_coefficient
        # cobra_reaction_object.gene_reaction_rule
        # cobra_reaction_object.user
        cobra_reaction_object.coefficients = coefficients
        return JsonResponse('test')


class AddDataMetaboliteToCobra(View):
    def post(self, request, database_pk):
        # user
        cobra_metabolite_object = data_metabolite_to_cobra_metabolite("pk", database_pk)
        cobra_metabolite_object.save()
        return JsonResponse("test")
