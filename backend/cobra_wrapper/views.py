import json

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from django.http import HttpResponseBadRequest, Http404
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from cobra.exceptions import OptimizationError

from .models import CobraModel, CobraReaction, CobraMetabolite


def get_models_by_id(model_type, pk_list, model_owner):
    try:
        return [model_type.objects.get(id=pk, owner=model_owner) for pk in pk_list]
    except model_type.DetailDoesNotExist:
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


class ListMixin:
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
            return HttpResponseBadRequest(json.dumps({
                'type': 'validation_error',
                'content': get_validation_error_content(error)
            }))
        return redirect(self.model.get_list_url())

    def get(self, request):
        return render(request, 'cobra_wrapper/{}/list.html'.format(self.model.MODEL_NAME), context={
            'all': self.model.objects.filter(owner=request.user)
        })


class CobraMetaboliteListView(LoginRequiredMixin, ListMixin, View):
    model = CobraMetabolite
    fields = ['cobra_id', 'name', 'formula', 'charge', 'compartment']
    related_field = None


class CobraReactionListView(LoginRequiredMixin, ListMixin, View):
    model = CobraReaction
    fields = [
        'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'coefficients',
        'gene_reaction_rule'
    ]
    related_field = {'name': 'metabolites', 'to': CobraMetabolite}


class CobraModelListView(LoginRequiredMixin, ListMixin, View):
    model = CobraModel
    fields = ['cobra_id', 'name', 'objective']
    related_field = {'name': 'reactions', 'to': CobraReaction}


class DetailMixin:
    http_method_names = ['get', 'post']

    model = None
    fields = []
    related_fields = {'name': None, 'to': None}

    def get(self, request, pk):
        return render(request, 'cobra_wrapper/{}/detail.html'.format(self.model.MODEL_NAME), context={
            self.model.MODEL_NAME: get_object_or_404(self.model, pk=pk, owner=request.user)
        })

    # def delete(self, request, pk):  # TODO
    #     try:
    #         self.model.objects.get(owner=request.user, id=pk).delete()
    #     except DetailDoesNotExist:
    #         return JsonResponse({}, status=404)
    #     return JsonResponse({}, status=204)

    # def patch(self, request, pk):
    #     content = json.loads(request.body)
    #     try:
    #         model = self.model.objects.get(owner=request.user, id=pk)
    #     except DetailDoesNotExist:
    #         return JsonResponse({}, status=404)

    #     for field in self.fields:
    #         if field in content.keys():
    #             setattr(model, field, content[field])

    #     try:
    #         model.save()
    #         if self.related_fields and self.related_fields['name'] in content.keys():
    #             getattr(model, self.related_fields['name']).set(
    #                 get_models_by_id(self.related_fields['to'], content[self.related_fields['name']], request.user))
    #     except ValidationError as error:
    #         return JsonResponse({
    #             'type': 'validation_error',
    #             'content': get_validation_error_content(error)
    #         })
    #     return JsonResponse({}, status=200)


class CobraMetaboliteDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraMetabolite
    fields = ['cobra_id', 'name', 'formula', 'charge', 'compartment']
    related_field = None


class CobraReactionDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraReaction
    fields = [
        'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'coefficients',
        'gene_reaction_rule'
    ]
    related_field = {'name': 'metabolites', 'to': CobraMetabolite}


class CobraModelDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraModel
    fields = ['cobra_id', 'name', 'objective']
    related_field = {'name': 'reactions', 'to': CobraReaction}


class CobraModelDetailComputeView(LoginRequiredMixin, View):

    def post(self, request, pk, method):
        content = json.loads(request.body)
        # model = get_object_or_404(CobraModel, pk=pk, user=request.user)

        try:
            if method == 'fba':
                # return JsonResponse(model.fba(), status=200)
                return  # TODO
            elif method == 'fva':
                # fva_params = try_get_fields(content, ['loopless', 'fraction_of_optimum', 'pfba_factor', 'processes'])

                try:
                    if 'reaction_list' in content.keys():
                        reactions = get_models_by_id(CobraReaction, content['reaction_list'], request.user)
                        content['reaction_list'] = []
                        for reaction in reactions:
                            content['reaction_list'].append(reaction.build())
                    # return JsonResponse(model.fva(reaction_list=content['reaction_list'], **fva_params), status=200)
                    return  # TODO
                except ValidationError as error:
                    return HttpResponseBadRequest(json.dumps({
                        'type': 'validation_error',
                        'content': {
                            'reaction_list': [
                                {
                                    'code': error.code,
                                    'message': error.message
                                }
                            ]
                        }
                    }))
            else:
                return Http404()
        except OptimizationError as error:
            return HttpResponseBadRequest(json.dumps({'code': 'cobra-error', 'message': error.args[0]}))
