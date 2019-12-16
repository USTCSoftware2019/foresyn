import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from .models import ShareModel
from cobra_wrapper.models import CobraModel
from cobra_wrapper.utils import load_sbml


class CreateShareLinkView(View):
    http_method_names = ['post']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.owner = None

    def recursive_create_link_for_model(self, model_id, desc):
        try:
            cobra_model = CobraModel.objects.get(id=model_id)
        except ObjectDoesNotExist:
            return None
        if cobra_model.owner != self.owner:
            return None
        shared_model_object = ShareModel.objects.create(sbml_content=cobra_model.sbml_content,
                                                        owner=self.owner,
                                                        name=cobra_model.name,
                                                        desc=desc,
                                                        reactions=cobra_model.reactions,
                                                        metabolites=cobra_model.metabolites,
                                                        genes=cobra_model.genes
                                                        )
        shared_model_object.save()
        return shared_model_object

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("/accounts/login")
        self.owner = request.user
        try:
            object_id = request.POST['model_id']
        except KeyError:
            return HttpResponse("required model_id", status=400)
        try:
            desc = request.POST['desc']
        except KeyError:
            desc = ""
        model_object = self.recursive_create_link_for_model(object_id, desc)
        if model_object is None:
            return JsonResponse({"messages": "error"}, status=400)
        url = "https://foresyn.tech/share/model/"
        return JsonResponse({"url": url + model_object.id.__str__()}, status=200)


class ModelShareView(DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(ShareModel, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data['reactions'] = json.loads(self.object.reactions)
        context_data['metabolites'] = json.loads(self.object.metabolites)
        context_data['genes'] = json.loads(self.object.genes)
        context_data['username'] = self.object.owner.username
        context_data["desc"] = self.object.desc
        context_data["id"] = self.object.id
        return context_data


class AddToMyModel(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("/accounts/login")
        user = request.user
        try:
            model_id = request.POST["id"]
        except KeyError:
            return HttpResponse("id required", status=400)
        try:
            share_model = ShareModel.objects.get(id=model_id)
        except ObjectDoesNotExist:
            return HttpResponse("No such model found", status=404)
        try:
            name = request.POST["name"]
        except KeyError:
            name = "new model"
        cobra_model_object = CobraModel()
        cobra_model_object.sbml_content = share_model.sbml_content
        cobra_model_object.owner = user

        print(cobra_model_object)
        cobra_model_object.name = name
        cobra_model_object.save()
        # cobra_model_object.cache(load_sbml(cobra_model_object.sbml_content))
        # return JsonResponse({"messages": "OK"}, status=200)
        return redirect("/cobra/models")
