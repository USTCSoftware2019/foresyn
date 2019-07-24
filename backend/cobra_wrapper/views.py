import json

from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from cobra.exceptions import OptimizationError

from .models import CobraModel, CobraReaction, CobraMetabolite
from .utils import get_possible_params


class CobraModelApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request):
        params = json.loads(request.body)
        try:
            reactions = [
                CobraReaction.objects.get(user=request.user, id=reaction_id)
                for reaction_id in params['reactions']
            ]
        except AttributeError:
            reactions = []
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        model = CobraModel(**get_possible_params(params, CobraModel.plain_fields), user=request.user)
        try:
            model.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        model.save()
        model.reactions.set(reactions)
        model.save()
        return JsonResponse({'id': model.id}, status=201)

    def get(self, request):
        if 'id' in request.GET.keys():
            try:
                return JsonResponse(
                    CobraModel.objects.get(user=request.user, id=request.GET['id'][0]).json(), status=200)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=404)
        else:
            return JsonResponse(
                {'models': [model.json() for model in CobraModel.objects.filter(user=request.user)]}, status=200)

    def delete(self, request):
        try:
            model = CobraModel.objects.get(user=request.user, id=json.loads(request.body)['id'])
        except AttributeError as error:
            return JsonResponse({'code': 100101, 'message': error.args[0]}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        model.delete()
        return JsonResponse({}, status=204)

    def patch(self, request):
        params = json.loads(request.body)
        try:
            model = CobraModel.objects.get(user=request.user, id=params['id'])
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        try:
            if 'reactions' in params.keys():
                reactions = [
                    CobraReaction.objects.get(user=request.user, id=reaction_id)
                    for reaction_id in params['reactions']
                ]
                model.reactions.set(reactions)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        for field in CobraModel.plain_fields:
            if field in params.keys():
                setattr(model, field, params[field])
        try:
            model.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        model.save()
        return JsonResponse({'id': model.id}, status=200)


class CobraReactionApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request):
        params = json.loads(request.body)
        try:
            metabolites = [
                CobraMetabolite.objects.get(user=request.user, id=metabolite_id)
                for metabolite_id in params['metabolites']
            ]
        except AttributeError:
            metabolites = []
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        reaction = CobraReaction(**get_possible_params(params, CobraReaction.plain_fields), user=request.user)
        if 'coefficients' in params.keys():
            reaction.coefficients = ' '.join(map(lambda num: str(num), params['coefficients']))
        try:
            reaction.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        reaction.save()
        reaction.metabolites.set(metabolites)
        reaction.save()
        return JsonResponse({'id': reaction.id}, status=201)

    def get(self, request):
        if 'id' in request.GET.keys():
            try:
                return JsonResponse(
                    CobraReaction.objects.get(user=request.user, id=request.GET['id'][0]).json(), status=200)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=404)
        else:
            return JsonResponse(
                {'reactions': list([reaction.json() for reaction in CobraReaction.objects.filter(user=request.user)])},
                status=200
            )

    def delete(self, request):
        try:
            reaction = CobraReaction.objects.get(user=request.user, id=json.loads(request.body)['id'])
        except AttributeError as error:
            return JsonResponse({'code': 100101, 'message': error.args[0]}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        reaction.delete()
        return JsonResponse({}, status=204)

    def patch(self, request):
        params = json.loads(request.body)
        try:
            reaction = CobraReaction.objects.get(user=request.user, id=params['id'])
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        try:
            if 'metabolites' in params.keys():
                metabolites = [
                    CobraMetabolite.objects.get(user=request.user, id=metabolite_id)
                    for metabolite_id in params['metabolites']
                ]
                reaction.metabolites.set(metabolites)
        except ObjectDoesNotExist as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        if 'coefficients' in params.keys():
            reaction.coefficients = ' '.join(map(lambda num: str(num), params['coefficients']))
        for field in CobraReaction.plain_fields:
            if field in params.keys():
                setattr(reaction, field, params[field])
        try:
            reaction.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        reaction.save()
        return JsonResponse({'id': reaction.id}, status=200)


class CobraMetaboliteApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request):
        params = json.loads(request.body)
        metabolite = CobraMetabolite(**get_possible_params(params, CobraMetabolite.plain_fields), user=request.user)
        try:
            metabolite.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        metabolite.save()
        return JsonResponse({'id': metabolite.id}, status=201)

    def get(self, request):
        if 'id' in request.GET.keys():
            try:
                return JsonResponse(
                    CobraMetabolite.objects.get(user=request.user, id=request.GET['id'][0]).json(), status=200)
            except ObjectDoesNotExist:
                return JsonResponse({}, status=404)
        else:
            return JsonResponse(
                {
                    'metabolites': [
                        metabolite.json() for metabolite in CobraMetabolite.objects.filter(user=request.user)
                    ]
                }, status=200
            )

    def delete(self, request):
        try:
            metabolite = CobraMetabolite.objects.get(user=request.user, id=json.loads(request.body)['id'])
        except AttributeError as error:
            return JsonResponse({'code': 100101, 'message': error.args[0]}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        metabolite.delete()
        return JsonResponse({}, status=204)

    def patch(self, request):
        params = json.loads(request.body)
        try:
            metabolite = CobraMetabolite.objects.get(user=request.user, id=params['id'])
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        for field in CobraModel.plain_fields:
            if field in params.keys():
                setattr(metabolite, field, params[field])
        try:
            metabolite.full_clean()
        except ValidationError as error:
            return JsonResponse({'code': 100101, 'message': error.messages[0]}, status=400)
        metabolite.save()
        return JsonResponse({'id': metabolite.id}, status=200)


class CobraComputeApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, model_id, method):
        params = json.loads(request.body)
        try:
            model = CobraModel.objects.get(user=request.user, id=model_id)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        try:
            if method == 'fba':
                return JsonResponse(model.fba(), status=200)
            elif method == 'fva':
                fva_params = get_possible_params(
                    params, ['loopless', 'fraction_of_optimum', 'pfba_factor', 'processes'])
                params['reaction_list'] = list(
                    [model.reactions.get(id=reaction_id).identifier for reaction_id in params['reaction_list']])
                return JsonResponse(
                    model.fva(reaction_list=params['reaction_list'], **fva_params), status=200)
            else:
                return JsonResponse({}, status=404)
        except OptimizationError as error:
            return JsonResponse({'code': 100102, 'message': error.args[0]}, status=400)
