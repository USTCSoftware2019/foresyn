from django.views import View

from cobra_wrapper.models import CobraModel, CobraMetabolite, CobraReaction
from bigg_database.models import Model as DataModel, Metabolite as DataMetabolite, Reaction as DataReaction
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .common import reaction_string_to_metabolites, data_metabolite_to_cobra_metabolite, data_reaction_to_cobra_reaction


class AddDataModelToCobra(View):
    def post(self, request, database_pk):
        datamodel_object = DataModel.objects.get(pk=database_pk)
        cobramodel_object = CobraModel()
        # relationship
        cobramodel_object.identifier = datamodel_object.bigg_id
        cobramodel_object.name = datamodel_object.bigg_id

        # add reactions first

        datamodel_reactions = datamodel_object.modelreaction_set
        for datareaction in datamodel_reactions.all():
            # waiting for test data...
            # TBD
            pass

        return JsonResponse("test")


class AddDataReactionToCobra(View):
    def post(self, request, database_pk):
        cobra_reaction_object = data_reaction_to_cobra_reaction(key="pk", value=database_pk)
        cobra_reaction_object.save()
        return JsonResponse('test')


class AddDataMetaboliteToCobra(View):
    def post(self, request, database_pk):
        # user
        cobra_metabolite_object = data_metabolite_to_cobra_metabolite("pk", database_pk)
        cobra_metabolite_object.save()
        return JsonResponse("test")
