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
        return [model_type.objects.get(id=int(pk), owner=model_owner) for pk in pk_list]
    except model_type.DetailDoesNotExist:
        raise ValidationError('invalid id in model id list', 'invalid')


def try_get_fields(content, fields):
    return {field: content[field] for field in fields if field in content.keys()}


def get_validation_error_content(error):
    return {
        field: [
            {
                'code': field_error.code,
                'message': str(field_error.message)
                # For Django uses lazy text
            }
            for field_error in error.error_dict[field]
        ]
        for field in error.error_dict.keys()
    }


def get_post_content(request):
    info = {field: value for field, value in request.POST.items()}
    for field in info.keys():
        if field in ['reaction', 'metabolites']:
            info[field] = [int(pk) for pk in info[field]]  # FIXME: May raise error

        if field in ['lower_bound', 'upper_bound', 'objective_coefficient']:
            if info[field]:
                info[field] = float(info[field])  # FIXME: See above
            else:
                info[field] = None
    return info


class ListMixin:
    http_method_names = ['get', 'post']

    model = None
    fields = []
    related_field = {'name': None, 'to': None}

    def post(self, request):
        content = get_post_content(request)
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
        return redirect(new_model)

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
    related_field = {'name': None, 'to': None}

    def get(self, request, pk):
        return render(request, 'cobra_wrapper/{}/detail.html'.format(self.model.MODEL_NAME), context={
            self.model.MODEL_NAME: get_object_or_404(self.model, pk=pk, owner=request.user),
            'related_models': self.related_field['to'].objects.filter(owner=request.user)
        })

    def post(self, request, pk):
        if 'delete' in request.POST.keys():
            return DetailMixin._delete(self, request, pk)
        elif 'edit' in request.POST.keys():
            return DetailMixin._patch(self, request, pk)
        else:
            return HttpResponseBadRequest('Unknown operation!')

    def _delete(self, request, pk):  # TODO
        get_object_or_404(self.model, owner=request.user, id=pk).delete()
        return redirect(self.model.get_list_url())

    def _patch(self, request, pk):
        content = get_post_content(request)
        model = get_object_or_404(self.model, owner=request.user, id=pk)

        for field in self.fields:
            if field in content.keys():
                setattr(model, field, content[field])

        try:
            model.save()
            if self.related_field and self.related_field['name'] in content.keys():
                getattr(model, self.related_field['name']).set(
                    get_models_by_id(self.related_field['to'], content[self.related_field['name']], request.user))
        except ValidationError as error:
            return HttpResponseBadRequest(json.dumps({
                'type': 'validation_error',
                'content': get_validation_error_content(error)
            }))

        return redirect(model)


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

    def get(self, request, pk, method):
        # content = json.loads(request.body)
        model = get_object_or_404(CobraModel, pk=pk, owner=request.user)

        try:
            if method == 'fba':
                # return JsonResponse(model.fba(), status=200)
                return render(request, 'cobra_wrapper/fba/detail.html', {"solution" : model.fba()})
            # elif method == 'fva':
            #     # fva_params = try_get_fields(content, ['loopless', 'fraction_of_optimum', 'pfba_factor', 'processes'])
            #
            #     try:
            #         if 'reaction_list' in content.keys():
            #             reactions = get_models_by_id(CobraReaction, content['reaction_list'], request.user)
            #             content['reaction_list'] = []
            #             for reaction in reactions:
            #                 content['reaction_list'].append(reaction.build())
            #         # return JsonResponse(model.fva(reaction_list=content['reaction_list'], **fva_params), status=200)
            #         return  # TODO
            #     except ValidationError as error:
            #         return HttpResponseBadRequest(json.dumps({
            #             'type': 'validation_error',
            #             'content': {
            #                 'reaction_list': [
            #                     {
            #                         'code': error.code,
            #                         'message': error.message
            #                     }
            #                 ]
            #             }
            #         }))
            else:
                return Http404()
        except OptimizationError as error:
            return HttpResponseBadRequest(json.dumps({'code': 'cobra-error', 'message': error.args[0]}))
