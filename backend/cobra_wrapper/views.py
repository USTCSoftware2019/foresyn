import json

from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from . import models as cobra_models


def get_params_from_request(request, param_list):
    return {param: json.loads(request.body)[param] for param in param_list}


class ModelView(View):
    def post(self, request):
        try:
            reactions = [
                cobra_models.CobraReaction.objects.get(id=reaction_id)
                for reaction_id in dict(
                    get_params_from_request(request, ['reactions'])
                )['reactions']
            ]
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200011,
                'message': error.message.pop()
            })
        cobra_model = cobra_models.CobraModel(
            **get_params_from_request(request, ['base', 'objective']))
        try:
            cobra_model.full_clean()
        except ValidationError as error:
            return JsonResponse({
                'code': 200001,
                'message': error.messages.pop()
            })
        cobra_model.save()
        cobra_model.reactions.set(reactions)
        cobra_model.save()
        return JsonResponse({'id': cobra_model.id}, status=201)

    def get(self, request):
        pass


class ReactionView(View):
    def post(self, request):
        try:
            metabolites = [
                cobra_models.CobraMetabolite.objects.get(id=metabolite_id)
                for metabolite_id in dict(
                    get_params_from_request(request, ['metabolites'])
                )['metabolites']
            ]
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200012,
                'message': error.message.pop()
            })
        cobra_reaction = cobra_models.CobraReaction(
            **get_params_from_request(request, [
                'base', 'name', 'subsystem', 'lower_bound', 'upper_bound',
                'coefficients', 'gene_reaction_rule'
            ])
        )
        try:
            cobra_reaction.full_clean()
        except ValidationError as error:
            return JsonResponse({
                'code': 200002,
                'message': error.messages.pop()
            })
        cobra_reaction.save()
        cobra_reaction.metabolites.set(metabolites)
        cobra_reaction.save()
        return JsonResponse({'id': cobra_reaction.id}, status=201)

    def get(self, request):
        pass


class MetaboliteView(View):
    def post(self, request):
        cobra_metabolite = cobra_models.CobraMetabolite(
            **get_params_from_request(request, [
                'base', 'formula', 'name', 'compartment'
            ])
        )
        try:
            cobra_metabolite.full_clean()
        except ValidationError as error:
            return JsonResponse({
                'code': 200003,
                'message': error.messages.pop()
            })
        cobra_metabolite.save()
        return JsonResponse({'id': cobra_metabolite.id}, status=201)

    def get(self, request):
        pass
