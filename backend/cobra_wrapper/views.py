import json

from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from cobra.exceptions import OptimizationError

from .models import CobraModel, CobraReaction, CobraMetabolite


def get_models_by_id(model_type, model_id_list, model_owner):
    try:
        return [model_type.objects.get(id=model_id, owner=model_owner) for model_id in model_id_list]
    except ObjectDoesNotExist:
        raise ValidationError('invalid id in id list', 'invalid-id')


def try_get_fields(content, fields):
    return {field: content[field] for field in fields if field in content.keys()}


class CobraMetaboliteSetApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request):
        content = json.loads(request.body)
        try:
            metabolite = CobraMetabolite.objects.create(**try_get_fields(content, [
                'cobra_id', 'name', 'formula', 'charge', 'compartment'
            ]), owner=request.user)
        except ValidationError as error:
            return JsonResponse({'code': error.code, 'message': error.messages[0]}, status=400)
        return JsonResponse({'id': metabolite.id}, status=201)

    def get(self, request):
        return JsonResponse(
            {'metabolites': [metabolite.json() for metabolite in CobraMetabolite.objects.filter(owner=request.user)]},
            status=200
        )


class CobraReactionSetApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request):
        content = json.loads(request.body)
        try:
            reaction = CobraReaction.objects.create(**try_get_fields(content, [
                'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'coefficients',
                'gene_reaction_rule'
            ]), owner=request.user)
            reaction.metabolites.set(get_models_by_id(CobraMetabolite, content.get('metabolites', []), request.user))
        except ValidationError as error:
            return JsonResponse({'code': error.code, 'message': error.messages[0]}, status=400)
        return JsonResponse({'id': reaction.id}, status=201)

    def get(self, request):
        return JsonResponse(
            {'reactions': [reaction.json() for reaction in CobraReaction.objects.filter(owner=request.user)]},
            status=200
        )


class CobraModelSetApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request):
        content = json.loads(request.body)
        try:
            model = CobraModel.objects.create(**try_get_fields(content, [
                'cobra_id', 'name', 'objective'
            ]), owner=request.user)
            model.reactions.set(get_models_by_id(CobraReaction, content.get('reactions', []), request.user))
        except ValidationError as error:
            return JsonResponse({'code': error.code, 'message': error.messages[0]}, status=400)
        return JsonResponse({'id': model.id}, status=201)

    def get(self, request):
        return JsonResponse(
            {'models': [model.json() for model in CobraModel.objects.filter(owner=request.user)]}, status=200)


class CobraMetaboliteObjectApi(LoginRequiredMixin, View):
    raise_exception = True

    def get(self, request, metabolite_id):
        try:
            return JsonResponse(CobraMetabolite.objects.get(owner=request.user, id=metabolite_id).json(), status=200)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)

    def delete(self, request, metabolite_id):
        try:
            CobraMetabolite.objects.get(owner=request.user, id=metabolite_id).delete()
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        return JsonResponse({}, status=204)

    def patch(self, request, metabolite_id):
        content = json.loads(request.body)
        try:
            metabolite = CobraMetabolite.objects.get(owner=request.user, id=metabolite_id)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)

        for field in ['cobra_id', 'name', 'formula', 'charge', 'compartment']:
            if field in content.keys():
                setattr(metabolite, field, content[field])

        try:
            metabolite.save()
        except ValidationError as error:
            return JsonResponse({'code': error.code, 'message': error.messages[0]}, status=400)
        return JsonResponse({}, status=200)


class CobraReactionObjectApi(LoginRequiredMixin, View):
    raise_exception = True

    def get(self, request, reaction_id):
        try:
            return JsonResponse(CobraReaction.objects.get(owner=request.user, id=reaction_id).json(), status=200)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)

    def delete(self, request, reaction_id):
        try:
            CobraReaction.objects.get(owner=request.user, id=reaction_id).delete()
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        return JsonResponse({}, status=204)

    def patch(self, request, reaction_id):
        content = json.loads(request.body)
        try:
            reaction = CobraReaction.objects.get(owner=request.user, id=reaction_id)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)

        for field in [
            'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'coefficients',
            'gene_reaction_rule'
        ]:
            if field in content.keys():
                setattr(reaction, field, content[field])

        try:
            reaction.save()
            if 'metabolites' in content.keys():
                reaction.metabolites.set(get_models_by_id(CobraMetabolite, content['metabolites'], request.user))
        except ValidationError as error:
            return JsonResponse({'code': error.code, 'message': error.messages[0]}, status=400)
        return JsonResponse({}, status=200)


class CobraModelObjectApi(LoginRequiredMixin, View):
    raise_exception = True

    def get(self, request, model_id):
        try:
            return JsonResponse(CobraModel.objects.get(owner=request.user, id=model_id).json(), status=200)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)

    def delete(self, request, model_id):
        try:
            CobraModel.objects.get(owner=request.user, id=model_id).delete()
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)
        return JsonResponse({}, status=204)

    def patch(self, request, model_id):
        content = json.loads(request.body)
        try:
            model = CobraModel.objects.get(owner=request.user, id=model_id)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)

        for field in ['cobra_id', 'name', 'objective']:
            if field in content.keys():
                setattr(model, field, content[field])

        try:
            if 'reactions' in content.keys():
                model.reactions.set(get_models_by_id(CobraReaction, content['reactions'], request.user))
            model.save()
        except ValidationError as error:
            return JsonResponse({'code': error.code, 'message': error.messages[0]}, status=400)
        return JsonResponse({}, status=200)


class CobraModelObjectComputeApi(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, model_id, method):
        content = json.loads(request.body)
        try:
            model = CobraModel.objects.get(owner=request.user, id=model_id)
        except ObjectDoesNotExist:
            return JsonResponse({}, status=404)

        try:
            if method == 'fba':
                return JsonResponse(model.fba(), status=200)
            elif method == 'fva':
                fva_params = try_get_fields(content, ['loopless', 'fraction_of_optimum', 'pfba_factor', 'processes'])

                try:
                    if 'reaction_list' in content.keys():
                        reactions = get_models_by_id(CobraReaction, content['reaction_list'], request.user)
                        content['reaction_list'] = []
                        for reaction in reactions:
                            content['reaction_list'].append(reaction.build())
                    return JsonResponse(model.fva(reaction_list=content['reaction_list'], **fva_params), status=200)
                except ValidationError as error:
                    return JsonResponse({'code': error.code, 'message': error.messages[0]}, status=400)
            else:
                return JsonResponse({}, status=404)
        except OptimizationError as error:
            return JsonResponse({'code': 'cobra-error', 'message': error.args[0]}, status=400)
