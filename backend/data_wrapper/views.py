import cobra

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.shortcuts import redirect
from cobra_wrapper.utils import load_sbml, dump_sbml
from bigg_database.models import Reaction as DataReaction
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
            return HttpResponse("bigg_id required", status=400)
        try:
            data_model_object = DataModel.objects.get(bigg_id=model_pk)
        except ObjectDoesNotExist:
            # return JsonResponse({"messages": "No such model found"}, status=404)
            return HttpResponse("No such model found", status=404)
        cobra_model_object = CobraModel()
        cobra_model_object.sbml_content = data_model_object.sbml_content
        cobra_model_object.owner = user
        try:
            name = request.POST["name"]
        except KeyError:
            name = "new model"
        try:
            desc = request.POST['desc']
        except KeyError:
            desc = "A new model"
        cobra_model_object.desc = desc
        cobra_model_object.name = name
        cobra_model_object.save()
        cobra_model_object.cache(load_sbml(cobra_model_object.sbml_content))
        # return JsonResponse({"messages": "OK"}, status=200)
        return redirect("/cobra/models")


class AddDataReactionToCobra(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("/accounts/login")
        user = request.user
        try:
            reaction_pk = request.POST["reaction_pk"]
        except KeyError:
            return HttpResponse("reaction pk required", status=400)
        try:
            model_pk = request.POST["model_pk"]
        except KeyError:
            return HttpResponse("model pk required", status=400)
        try:
            cobra_model_object = CobraModel.objects.get(pk=model_pk)
        except ObjectDoesNotExist:
            return HttpResponse("No model found", status=404)
        if cobra_model_object.owner != user:
            return HttpResponse("Not your model", status=403)

        try:
            data_reaction_object = DataReaction.objects.get(pk=reaction_pk)
        except ObjectDoesNotExist:
            return HttpResponse("No reaction found", status=404)
        reaction = cobra.Reaction(data_reaction_object.bigg_id)
        reaction.name = data_reaction_object.name
        metabolites_dict = reaction_string_to_metabolites(data_reaction_object.reaction_string)

        if metabolites_dict is None:
            return HttpResponse("Internal Error", status=500)
        reaction.add_metabolites(metabolites_dict)
        cobra_object = load_sbml(cobra_model_object.sbml_content)
        reaction.gene_reaction_rule = [gene.gene_reaction_rule for gene in data_reaction_object.reactiongene_set.all()][
            0]
        cobra_model_object.sbml_content = dump_sbml(cobra_object)
        cobra_model_object.save()
        cobra_model_object.cache(load_sbml(cobra_model_object.sbml_content))
        # return JsonResponse({"messages": "OK"}, status=200)
        return redirect("/cobra/models/" + str(cobra_model_object.pk))
