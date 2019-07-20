from django.views import View
from django.http import JsonResponse
from .models import Model,Reaction,Metabolite

class GetIdModel(View):
    def post(self,request):
        try:
            bigg_id = request.POST.get('bigg_id')
        except ValueError:
            pass
        
        model_instance = Model.objects.get(bigg_id=bigg_id)

        mod_ins = {
            "bigg_id":bigg_id,
            "compartments":model_instance.compartments,
            "version",model_instance.version,
        }

        return JsonResponse(json.dumps(mod_ins))
    
    def get(self,request):
        pass

class GetIdReaction(View):
    def post(self,request):
        try:
            bigg_id = request.POST.get('bigg_id')
        except ValueError:
            pass

        reaction_instance = Reaction.objects.get(bigg_id=bigg_id)

        reac_ins = {
            "bigg_id":bigg_id,
            "name":reaction_instance.name,
            "reaction_string":reaction_instance.reaction_string,
            "pseudoreaction":reaction_instance.pseudoreaction,
            "database_links":reaction_instance.database_links,
        }
        return JsonResponse(json.dumps(reac_ins))

    def get(self,request):
        pass

class GetIdMetabolite(View):
    def post(self,reqeust):
        try:
            bigg_id = request.POST.get('bigg_id')
        except ValueError:
            pass

        metabolite_instance = Metabolite.objects.get(bigg_id=bigg_id)

        meta_ins = {
            "bigg_id":bigg_id,
            "name":metabolite_instance.name,
            "formulae":metabolite_instance.formulae,
            "charges":metabolite_instance.charges,
            "database_links":metabolite_instance.database_links,
        }
        return JsonResponse(json.dumps(meta_ins))

    def get(self,request):
        pass
        
