from django.views import View
from cobra_wrapper.models import CobraModel, CobraMetabolite
from bigg_database.models import Model as DataModel, ModelReaction
from django.http import JsonResponse
from .common import data_metabolite_to_cobra_metabolite, data_reaction_to_cobra_reaction, reaction_string_to_metabolites
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import time


class AddDataModelToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"messages": "login required"}, status=401)
        user = request.user
        try:
            model_pk = request.POST["model_pk"]
        except KeyError:
            return JsonResponse({"messages": "pk required"}, status=400)
        # print(time.time())
        try:
            data_model_object = DataModel.objects.get(pk=model_pk)
        except ObjectDoesNotExist:
            return JsonResponse({"messages": "No such model found"}, status=404)
        cobra_model_object = CobraModel()
        # relationship
        cobra_model_object.identifier = data_model_object.bigg_id
        cobra_model_object.name = data_model_object.bigg_id

        cobra_model_object.owner = user
        cobra_model_object.cobra_id = data_model_object.bigg_id
        cobra_model_object.objective = ''
        cobra_model_object.save()

        # add reactions & metabolites
        for data_reaction in data_model_object.reaction_set.all():
            try:
                data_model_reaction = ModelReaction.objects.get(model=data_model_object, reaction=data_reaction)
            except ObjectDoesNotExist:
                return JsonResponse({"messages": "reaction not found"}, status=500)
            except MultipleObjectsReturned:
                return JsonResponse({"messages": "unknown error"}, status=500)
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

        # print(time.time())
        return JsonResponse({"messages": "OK"}, status=200)


class AddDataReactionToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"messages": "login required"}, status=401)
        user = request.user
        try:
            model_pk = request.POST["model_pk"]
            reaction_pk = request.POST["reaction_pk"]
        except KeyError:
            return JsonResponse({"messages": "pk required"}, status=400)
        cobra_reaction_object = data_reaction_to_cobra_reaction(key="pk", value=reaction_pk, user=user)
        if cobra_reaction_object is None:
            return JsonResponse({"messages": "no reactions"}, status=500)
        cobra_reaction_object.save()
        try:
            cobra_model_object = CobraModel.objects.get(pk=model_pk)
        except ObjectDoesNotExist:
            return JsonResponse({"messages": "no model found"}, status=500)
        cobra_model_object.reactions.add(cobra_reaction_object)
        return JsonResponse({"messages": "OK"}, status=200)


class AddDataMetaboliteToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"messages": "login required"}, status=401)
        user = request.user
        try:
            metabolite_pk = request.POST["pk"]  # SEE: <myl7> tests.test_add_metabolite
        except KeyError:
            return JsonResponse({"messages": "pk required"}, status=400)
        cobra_metabolite_object = data_metabolite_to_cobra_metabolite(key="pk", value=metabolite_pk, user=user)
        if cobra_metabolite_object is None:
            return JsonResponse({"messages": "no metabolite found"}, status=500)
        try:
            CobraMetabolite.objects.get(owner_id=user.id, cobra_id=cobra_metabolite_object.cobra_id)
            return JsonResponse({"messages": "metabolite already exist"}, status=200)
        except ObjectDoesNotExist:
            cobra_metabolite_object.save()
        return JsonResponse({"messages": "OK"}, status=200)
