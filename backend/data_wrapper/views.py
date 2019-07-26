from django.views import View

from cobra_wrapper.models import CobraModel
from bigg_database.models import Model as DataModel
from django.http import JsonResponse
from .common import data_metabolite_to_cobra_metabolite, data_reaction_to_cobra_reaction


class AddDataModelToCobra(View):
    def post(self, request, database_pk):
        # user = request.user
        data_model_object = DataModel.objects.get(pk=database_pk)
        cobra_model_object = CobraModel()
        # relationship
        cobra_model_object.identifier = data_model_object.bigg_id
        cobra_model_object.name = data_model_object.bigg_id

        # add reactions first

        for data_modelreaction in data_model_object.modelreaction_set.all():
            for data_reaction_object in data_modelreaction.reaction_set.all():
                cobra_reaction_object = data_reaction_to_cobra_reaction(
                    # user=user,
                    data_reaction_object=data_reaction_object,
                    subsystem=data_modelreaction.subsystem,
                    upper_bound=data_modelreaction.upper_bound,
                    lower_bound=data_modelreaction.lower_bound
                )
                cobra_reaction_object.save()

        # cobra_model_object.user = user
        cobra_model_object.save()
        return JsonResponse("test")


class AddDataReactionToCobra(View):
    def post(self, request):
        # user = request.user
        database_pk = request.POST["pk"]
        cobra_reaction_object = data_reaction_to_cobra_reaction(key="pk", value=database_pk)
        cobra_reaction_object.save()
        return JsonResponse('test')


class AddDataMetaboliteToCobra(View):
    def post(self, request):
        # user = request.user
        database_pk = request.POST["pk"]
        cobra_metabolite_object = data_metabolite_to_cobra_metabolite(key="pk", value=database_pk)
        cobra_metabolite_object.save()
        return JsonResponse("test")
