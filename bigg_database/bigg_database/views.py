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
<<<<<<< HEAD
            "bigg_id":model_instance.bigg_id,
            "compartments":model_instance.compartments,
            "version",model_instance.version,
=======
            "bigg_id": bigg_id,
            "compartments": model_instance.compartments,
            "version": model_instance.version,
>>>>>>> 026f63c665863fc138df48494c5ba6966eae70c8
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
<<<<<<< HEAD
            "bigg_id":reaction_instance.bigg_id,
            "name":reaction_instance.name,
            "reaction_string":reaction_instance.reaction_string,
            "pseudoreaction":reaction_instance.pseudoreaction,
            "database_links":reaction_instance.database_links,
=======
            "bigg_id": bigg_id,
            "name": reaction_instance.name,
            "reaction_string": reaction_instance.reaction_string,
            "pseudoreaction": reaction_instance.pseudoreaction,
            "database_links": reaction_instance.database_links,
>>>>>>> 026f63c665863fc138df48494c5ba6966eae70c8
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
<<<<<<< HEAD
            "bigg_id":metabolite_instance.bigg_id,
            "name":metabolite_instance.name,
            "formulae":metabolite_instance.formulae,
            "charges":metabolite_instance.charges,
            "database_links":metabolite_instance.database_links,
        }
        return JsonResponse(json.dumps(meta_ins))

    def get(self,request):
        pass


"""class GetModelByName(View):
    def post(self,request):
        try:
            name = request.POST.get('name')
        except ValueError:
            pass
        
        model_instance = Model.objects.get(name=name)

        mod_ins = {
            "bigg_id":bigg_id,
            "compartments":model_instance.compartments,
            "version",model_instance.version,
        }

        return JsonResponse(json.dumps(mod_ins))
    
    def get(self,request):
        pass""" # model不含name

class GetReactionByName(View):
    def post(self,request):
        try:
            name = request.POST.get('name')
        except ValueError:
            pass

        reaction_instance = Reaction.objects.get(name=name)

        reac_ins = {
            "bigg_id":reaction_instance.bigg_id,
            "name":reaction_instance.name,
            "reaction_string":reaction_instance.reaction_string,
            "pseudoreaction":reaction_instance.pseudoreaction,
            "database_links":reaction_instance.database_links,
        }
        return JsonResponse(json.dumps(reac_ins))

    def get(self,request):
        pass

class GetMetaboliteByName(View):
    def post(self,reqeust):
        try:
            name = request.POST.get('name')
        except ValueError:
            pass

        metabolite_instance = Metabolite.objects.get(name=name)

        meta_ins = {
            "bigg_id":metabolite_instance.bigg_id,
            "name":metabolite_instance.name,
            "formulae":metabolite_instance.formulae,
            "charges":metabolite_instance.charges,
            "database_links":metabolite_instance.database_links,
=======
            "bigg_id": bigg_id,
            "name": metabolite_instance.name,
            "formulae": metabolite_instance.formulae,
            "charges": metabolite_instance.charges,
            "database_links": metabolite_instance.database_links,
        }
        return JsonResponse({'code': 200, 'content': json.dumps(meta_ins)})


MATCH_RATIO = 80  # 相似率大于多少时返回


def fuzzy_search(query_set, request_name, request_data):
    ret_list = []
    # TODO
    # 提高效率
    for instance in query_set:
        if fuzz.ratio(getattr(instance, request_name), request_data) > MATCH_RATIO:
            ret_list.append(instance)

    return ret_list


class GetReactionFromName(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            name = request.POST['name']
        except KeyError:
            return JsonResponse({
                'code': 400,
                'content': _('name_Required')
            })

        match_list = fuzzy_search(Reaction.objects.all(), 'name', name)

        ret_content = [{
            "bigg_id": model_instance.bigg_id,
            "name": model_instance.name,
            "compartments": model_instance.compartments,
            "version": model_instance.version
        }
            for model_instance in match_list
        ]

        return JsonResponse({
            'code': 200,
            'content': ret_content
        })


class GetMetaboliteFromName(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            name = request.POST['name']
        except KeyError:
            return JsonResponse({
                'code': 400,
                'content': _('name_Required')
            })

        match_list = fuzzy_search(Metabolite.objects.all(), 'name', name)

        ret_content = [{
            "bigg_id": metabolite_instance.bigg_id,
            "name": metabolite_instance.name,
            "formulae": metabolite_instance.formulae,
            "charges": metabolite_instance.charges,
            "database_links": metabolite_instance.database_links,
>>>>>>> 026f63c665863fc138df48494c5ba6966eae70c8
        }
            for metabolite_instance in match_list
        ]

        return JsonResponse({
            'code': 200,
            'content': ret_content
        })
