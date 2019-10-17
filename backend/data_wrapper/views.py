import cobra

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views import View
from django.shortcuts import redirect
from cobra_wrapper.utils import load_sbml, dump_sbml
from bigg_database.models import Model as DataModel, Reaction as DataReaction
from cobra_wrapper.models import CobraModel
from .common import reaction_string_to_metabolites
from .models import DataModel


class AddDataModelToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            # return JsonResponse({"messages": "login required"}, status=401)
            return redirect("/accounts/login")
        user = request.user
        try:
            model_pk = request.POST["model_bigg_id"]
        except KeyError:
            # return JsonResponse({"messages": "bigg_id required"}, status=400)
            return redirect("")
        try:
            data_model_object = DataModel.objects.get(bigg_id=model_pk)
        except ObjectDoesNotExist:
            # return JsonResponse({"messages": "No such model found"}, status=404)
            return redirect("")
        cobra_model_object = CobraModel()
        cobra_model_object.sbml_content = data_model_object.sbml_content
        cobra_model_object.owner = user
        try:
            name = request.POST["name"]
        except KeyError:
            name = "new model"
        cobra_model_object.name = name
        cobra_model_object.save()
        # return JsonResponse({"messages": "OK"}, status=200)
        return redirect("/cobra/models")


class AddDataReactionToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            # return JsonResponse({"messages": "login required"}, status=401)
            return redirect("/accounts/login")
        user = request.user
        try:
            model_pk = request.POST["model_pk"]
            reaction_pk = request.POST["reaction_pk"]
        except KeyError:
            # return JsonResponse({"messages": "pk required"}, status=400)
            return redirect("")
        try:
            cobra_model_object = CobraModel.objects.get(pk=model_pk)
        except ObjectDoesNotExist:
            # return JsonResponse({"messages": "model not found"}, status=404)
            return redirect("")
        if cobra_model_object.owner is not user:
            return redirect("")

        try:
            data_reaction_object = DataReaction.objects.get(pk=reaction_pk)
        except ObjectDoesNotExist:
            # return JsonResponse({"messages": "reaction not found"}, status=404)
            return redirect("")
        reaction = cobra.Reaction(data_reaction_object.bigg_id)
        metabolites_dict = reaction_string_to_metabolites(data_reaction_object.reaction_string)
        reaction.add_metabolites(metabolites_dict)
        cobra_object = load_sbml(cobra_model_object.sbml_content)
        reaction.gene_reaction_rule = [gene.gene_reaction_rule for gene in data_reaction_object.reactiongene_set.all()]
        cobra_object.add_reactions([reaction])
        sbml_content = dump_sbml(cobra_object)
        cobra_model_object.sbml_content = sbml_content
        # return JsonResponse({"messages": "OK"}, status=200)
        return redirect("/cobra/models")
