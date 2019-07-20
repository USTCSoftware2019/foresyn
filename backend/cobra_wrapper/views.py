import json

from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from .models import CobraModel, CobraReaction, CobraMetabolite


def get_required_params(params, required_params):
    return {param: params[param] for param in required_params}


class CobraModelApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            reactions = [CobraReaction.objects.get(id=reaction_id) for reaction_id in params['reactions']]
            model = CobraModel(**get_required_params(params, ['identifier', 'objective']))
            model.full_clean()
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        except AttributeError as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        except ValidationError as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        model.save()
        model.reactions.set(reactions)
        model.save()
        return JsonResponse({'id': model.id}, status=201)

    def get(self, request):
        pass

    def delete(self, request):
        try:
            model_id = json.loads(request.body)['id']
        except AttributeError as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        try:
            model = CobraModel.objects.get(id=model_id)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        model.delete()
        return JsonResponse({}, status=204)

    def patch(self, request):
        params = json.loads(request.body)
        try:
            model = CobraModel.objects.get(id=params['id'])
            if 'reactions' in params.keys():
                reactions = [CobraReaction.objects.get(id=reaction_id) for reaction_id in params['reactions']]
                model.reactions.set(reactions)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        for field in ['identifier', 'objective']:
            if field in params.keys():
                setattr(model, field, params[field])
        try:
            model.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        model.save()
        return JsonResponse({'id': model.id}, status=200)


class CobraReactionApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            metabolites = [CobraMetabolite.objects.get(id=metabolite_id) for metabolite_id in params['metabolites']]
            reaction = CobraReaction(**get_required_params(params, [
                'identifier', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'gene_reaction_rule']))
            reaction.coefficients = ' '.join(map(lambda num: str(num), params['coefficients']))
            reaction.full_clean()
        except AttributeError as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        except ValidationError as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        reaction.save()
        reaction.metabolites.set(metabolites)
        reaction.save()
        return JsonResponse({'id': reaction.id}, status=201)

    def get(self, request):
        pass

    def delete(self, request):
        try:
            reaction_id = json.loads(request.body)['id']
        except AttributeError as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        try:
            reaction = CobraReaction.objects.get(id=reaction_id)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        reaction.delete()
        return JsonResponse({}, status=204)

    def patch(self, request):
        params = json.loads(request.body)
        try:
            reaction = CobraReaction.objects.get(id=params['id'])
            if 'metabolites' in params.keys():
                metabolites = [
                    CobraMetabolite.objects.get(id=metabolite_id) for metabolite_id in params['metabolites']]
                reaction.metabolites.set(metabolites)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        for field in ['identifier', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'gene_reaction_rule']:
            if field in params.keys():
                setattr(reaction, field, params[field])
        if 'coefficients' in params.keys():
            reaction.coefficients = ' '.join(map(lambda num: str(num), params['coefficients']))
        try:
            reaction.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        reaction.save()
        return JsonResponse({'id': reaction.id}, status=200)


class CobraMetaboliteApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            metabolite = CobraMetabolite(**get_required_params(params, [
                'identifier', 'formula', 'name', 'compartment']))
            metabolite.full_clean()
        except AttributeError as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        except ValidationError as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        metabolite.save()
        return JsonResponse({'id': metabolite.id}, status=201)

    def get(self, request):
        pass

    def delete(self, request):
        try:
            metabolite_id = json.loads(request.body)['id']
        except AttributeError as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        try:
            metabolite = CobraMetabolite.objects.get(id=metabolite_id)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        metabolite.delete()
        return JsonResponse({}, status=204)

    def patch(self, request):
        params = json.loads(request.body)
        try:
            metabolite = CobraMetabolite.objects.get(id=params['id'])
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        for field in ['identifier', 'formula', 'name', 'compartment']:
            if field in params.keys():
                setattr(metabolite, field, params[field])
        try:
            metabolite.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100000, 'message': error.messages}, status=400)
        metabolite.save()
        return JsonResponse({'id': metabolite.id}, status=200)


class CobraComputeApi(View):
    def get(self, request, method):
        try:
            model_id = request.GET['id'][0]
        except AttributeError as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        try:
            model = CobraModel.objects.get(id=model_id)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        try:
            cobra_model = model.build()
        except Exception as error:
            return JsonResponse({'code': 100000, 'message': error.args}, status=400)
        cobra_model  # todo
