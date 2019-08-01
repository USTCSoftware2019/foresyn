from django.views import View
from cobra_wrapper.models import CobraModel
from bigg_database.models import Model as DataModel, ModelReaction
from django.http import JsonResponse
from .common import data_metabolite_to_cobra_metabolite, data_reaction_to_cobra_reaction
from django.core.exceptions import ObjectDoesNotExist


class AddDataModelToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"messages": "login required"}, status=401)
        user = request.user
        database_pk = request.POST["pk"]
        data_model_object = DataModel.objects.get(pk=database_pk)
        cobra_model_object = CobraModel()
        # relationship
        cobra_model_object.identifier = data_model_object.bigg_id
        cobra_model_object.name = data_model_object.bigg_id

        cobra_model_object.owner = user
        cobra_model_object.cobra_id = data_model_object.bigg_id
        cobra_model_object.objective = ''
        cobra_model_object.save()

        for data_reaction in data_model_object.reaction_set.all():
            data_model_reaction = ModelReaction.objects.get(model=data_model_object, reaction=data_reaction)
            cobra_reaction_object = data_reaction_to_cobra_reaction(
                user=user,
                data_reaction_object=data_reaction,
                subsystem=data_model_reaction.subsystem,
                upper_bound=data_model_reaction.upper_bound,
                lower_bound=data_model_reaction.lower_bound
            )
            if cobra_reaction_object is None:
                return JsonResponse({"messages": "cobra_reaction_object is null"}, status=500)
            cobra_reaction_object.save()
            cobra_model_object.reactions.add(cobra_reaction_object)

        return JsonResponse({"messages":"OK"}, status=200)


class AddDataReactionToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"messages": "login required"}, status=401)
        user = request.user
        database_pk = request.POST["pk"]
        cobra_reaction_object = data_reaction_to_cobra_reaction(key="pk", value=database_pk, user=user)
        if cobra_reaction_object is None:
            return JsonResponse({"messages": "no reactions"}, status=500)
        cobra_reaction_object.save()
        return JsonResponse({"messages": "OK"}, status=200)


class AddDataMetaboliteToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"messages": "login required"}, status=401)
        user = request.user
        database_pk = request.POST["pk"]
        cobra_metabolite_object = data_metabolite_to_cobra_metabolite(key="pk", value=database_pk, user=user)
        if cobra_metabolite_object is None:
            return JsonResponse({"messages": "no metabolite found"}, status=500)
        try:
            CobraModel.objects.get(user=user, cobra_id=cobra_metabolite_object.cobra_id)
            return JsonResponse({"messages": "metabolite already exist"}, status=200)
        except ObjectDoesNotExist:
            cobra_metabolite_object.save()
        return JsonResponse({"messages": "OK"}, status=200)
