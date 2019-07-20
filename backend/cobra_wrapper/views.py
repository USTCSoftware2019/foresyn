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
            reactions = [
                CobraReaction.objects.get(id=reaction_id)
                for reaction_id in params['reactions']
            ]
            model = CobraModel(**get_required_params(params, [
                'identifier', 'objective'
            ]))
            model.full_clean()
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200021,
                'message': error.messages
            }, status=400)
        except AttributeError as error:
            return JsonResponse({
                'code': 200011,
                'message': error.args
            }, status=400)
        except ValidationError as error:
            return JsonResponse({
                'code': 200001,
                'message': error.messages
            }, status=400)
        model.save()
        model.reactions.set(reactions)
        model.save()
        return JsonResponse({'id': model.id}, status=201)

    def get(self, request):
        pass


class CobraReactionApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            metabolites = [
                CobraMetabolite.objects.get(id=metabolite_id)
                for metabolite_id in params['metabolites']
            ]
            reaction = CobraReaction(
                **get_required_params(params, [
                    'identifier', 'name', 'subsystem', 'lower_bound', 'upper_bound',
                    'coefficients', 'gene_reaction_rule'
                ])
            )
            reaction.full_clean()
        except AttributeError as error:
            return JsonResponse({
                'code': 200022,
                'message': error.args
            }, status=400)
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200012,
                'message': error.messages
            }, status=400)
        except ValidationError as error:
            return JsonResponse({
                'code': 200002,
                'message': error.messages
            }, status=400)
        reaction.save()
        reaction.metabolites.set(metabolites)
        reaction.save()
        return JsonResponse({'id': reaction.id}, status=201)

    def get(self, request):
        pass


class CobraMetaboliteApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            metabolite = CobraMetabolite(
                **get_required_params(params, [
                    'identifier', 'formula', 'name', 'compartment'
                ])
            )
            metabolite.full_clean()
        except AttributeError as error:
            return JsonResponse({
                'code': 200013,
                'message': error.args
            }, status=400)
        except ValidationError as error:
            return JsonResponse({
                'code': 200003,
                'message': error.messages
            }, status=400)
        metabolite.save()
        return JsonResponse({'id': metabolite.id}, status=201)

    def get(self, request):
        pass
