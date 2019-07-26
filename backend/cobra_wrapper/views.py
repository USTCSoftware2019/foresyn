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
        raise ValidationError('invalid id in model id list', 'invalid')


def try_get_fields(content, fields):
    return {field: content[field] for field in fields if field in content.keys()}


def get_validation_error_content(error):
    return {
        field: [
            {
                'code': field_error.code,
                'message': field_error.message
            }
            for field_error in error.error_dict[field]
        ]
        for field in error.error_dict.keys()
    }


class SetMixin:
    http_method_names = ['get', 'post']

    model = None
    fields = []
    related_field = {'name': None, 'to': None}

    def post(self, request):
        content = json.loads(request.body)
        try:
            new_model = self.model.objects.create(**try_get_fields(content, self.fields), owner=request.user)
            if self.related_field:
                getattr(new_model, self.related_field['name']).set(
                    get_models_by_id(
                        self.related_field['to'], content.get(self.related_field['name'], []), request.user)
                )
        except ValidationError as error:
            return JsonResponse({
                'type': 'validation_error',
                'content': get_validation_error_content(error)
            }, status=400)
        return JsonResponse({'id': new_model.id}, status=201)

    def get(self, request):
        return JsonResponse(
            {'all': [model.json() for model in self.model.objects.filter(owner=request.user)]}, status=200)


class CobraMetaboliteSetApi(SetMixin, LoginRequiredMixin, View):
    model = CobraMetabolite
    fields = ['cobra_id', 'name', 'formula', 'charge', 'compartment']
    related_field = None


class CobraReactionSetApi(SetMixin, LoginRequiredMixin, View):
    model = CobraReaction
    fields = [
        'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'coefficients',
        'gene_reaction_rule'
    ]
    related_field = {'name': 'metabolites', 'to': CobraMetabolite}


class CobraModelSetApi(SetMixin, LoginRequiredMixin, View):
    model = CobraModel
    fields = ['cobra_id', 'name', 'objective']
    related_field = {'name': 'reactions', 'to': CobraReaction}


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
            return JsonResponse({
                'type': 'validation_error',
                'content': get_validation_error_content(error)
            }, status=400)
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
            return JsonResponse({
                'type': 'validation_error',
                'content': get_validation_error_content(error)
            }, status=400)
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
            return JsonResponse({
                'type': 'validation_error',
                'content': get_validation_error_content(error)
            }, status=400)
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
                    return JsonResponse({
                        'type': 'validation_error',
                        'content': get_validation_error_content(error)
                    }, status=400)
            else:
                return JsonResponse({}, status=404)
        except OptimizationError as error:
            return JsonResponse({'code': 'cobra-error', 'message': error.args[0]}, status=400)
