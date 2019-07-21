import json
from fuzzywuzzy import fuzz

from django.http import JsonResponse
from django.views import View
from django.utils.translation import gettext as _

from .models import Metabolite, Model, Reaction


class GetModelFromId(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            bigg_id = request.POST['bigg_id']
        except KeyError:
            return JsonResponse({
                'code': 400,
                'content': _('bigg_id_Required')
            })

        model_instance = Model.objects.get(bigg_id=bigg_id)

        mod_ins = {
            "bigg_id":model_instance.bigg_id,
            "compartments":model_instance.compartments,
            "version":model_instance.version,
        }

        return JsonResponse({'code': 200, 'content': json.dumps(mod_ins)})


class GetReactionFromId(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            bigg_id = request.POST['bigg_id']
        except KeyError:
            return JsonResponse({
                'code': 400,
                'content': _('bigg_id_Required')
            })

        reaction_instance = Reaction.objects.get(bigg_id=bigg_id)

        reac_ins = {
            "bigg_id":reaction_instance.bigg_id,
            "name":reaction_instance.name,
            "reaction_string":reaction_instance.reaction_string,
            "pseudoreaction":reaction_instance.pseudoreaction,
            "database_links":reaction_instance.database_links,
        }
        return JsonResponse({'code': 200, 'content': json.dumps(reac_ins)})


class GetMetaboliteFromId(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            bigg_id = request.POST['bigg_id']
        except KeyError:
            return JsonResponse({
                'code': 400,
                'content': _('bigg_id_Required')
            })

        metabolite_instance = Metabolite.objects.get(bigg_id=bigg_id)

        meta_ins = {
            "bigg_id":metabolite_instance.bigg_id,
            "name":metabolite_instance.name,
            "formulae":metabolite_instance.formulae,
            "charges":metabolite_instance.charges,
            "database_links":metabolite_instance.database_links,
        }
        return JsonResponse({'code': 200, 'content': json.dumps(meta_ins)})



class GetReactionFromName(View):
    http_method_names = ['post']

    def post(self,request):
        try:
            name = request.POST.get('name')
        except KeyError:
            return JsonResponse({
                'code': 400,
                'content': _('name_Required')
            })

        reaction_instance = Reaction.objects.get(name=name)

        reac_ins = {
            "bigg_id":reaction_instance.bigg_id,
            "name":reaction_instance.name,
            "reaction_string":reaction_instance.reaction_string,
            "pseudoreaction":reaction_instance.pseudoreaction,
            "database_links":reaction_instance.database_links,
        }
        return JsonResponse({'code': 200, 'content': json.dumps(reac_ins)})


class GetMetaboliteFromName(View):
    http_method_names = ['post']

    def post(self,reqeust):
        try:
            name = request.POST.get('name')
        except KeyError:
            return JsonResponse({
                'code': 400,
                'content': _('name_Required')
            })

        metabolite_instance = Metabolite.objects.get(name=name)

        meta_ins = {
            "bigg_id":metabolite_instance.bigg_id,
            "name":metabolite_instance.name,
            "formulae":metabolite_instance.formulae,
            "charges":metabolite_instance.charges,
            "database_links":metabolite_instance.database_links,
        }

        return JsonResponse({'code': 200, 'content': json.dumps(meta_ins)})
