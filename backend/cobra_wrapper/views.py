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


def get_request_content(method, request):
    info = {field: value for field, value in getattr(request, method).items()}

    is_to_pop_metabolites_and_coefficients = False

    for field in info.keys():
        if field in ['reactions', 'metabolites', 'reaction_list']:
            try:
                info[field] = [int(pk) for pk in getattr(request, method).getlist(field)]
            except ValueError:
                pass

        if field in ['lower_bound', 'upper_bound', 'objective_coefficient', 'pfba_factor']:
            if info[field]:
                try:
                    info[field] = float(info[field])
                except ValueError:
                    pass
            else:
                info[field] = None

        if field == 'fraction_of_optimum':
            try:
                info[field] = float(info[field])
            except ValueError:
                pass

        if field == 'coefficients':
            if 'metabolites' not in info.keys() or not info[field]:
                is_to_pop_metabolites_and_coefficients = True
            else:
                try:
                    info[field] = json.loads(info[field])
                except json.decoder.JSONDecodeError:
                    pass

    if is_to_pop_metabolites_and_coefficients:
        info.pop('metabolites', None)
        info.pop('coefficients', None)

    return info


class ListMixin:
    http_method_names = ['get', 'post']

    model = None
    fields = []

    relation_field = None
    to_model = None

    def post(self, request):
        content = get_request_content('GET', request)
        try:
            new_model = self.model.objects.create(**try_get_fields(content, self.fields), owner=request.user)
            if self.relation_field:
                getattr(new_model, self.relation_field).set(
                    get_models_by_id(self.to_model, content.get(self.relation_field, []), request.user)
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


class CobraReactionListView(LoginRequiredMixin, ListMixin, View):
    model = CobraReaction
    fields = [
        'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'coefficients',
        'gene_reaction_rule'
    ]

    relation_field = 'metabolites'
    to_model = CobraMetabolite


class CobraModelListView(LoginRequiredMixin, ListMixin, View):
    model = CobraModel
    fields = ['cobra_id', 'name', 'objective']

    relation_field = 'reactions'
    to_model = CobraReaction


class DetailMixin:
    http_method_names = ['get', 'post']

    model = None
    fields = []

    relation_field = None
    to_model = None
    from_model = None

    def get(self, request, pk):
        return render(request, 'cobra_wrapper/{}/detail.html'.format(self.model.MODEL_NAME), context={
            self.model.MODEL_NAME: get_object_or_404(self.model, pk=pk, owner=request.user),
            'related_models': (self.to_model.objects.filter(owner=request.user) if self.relation_field else None)
        })

    def post(self, request, pk):
        if 'delete' in request.POST.keys():
            return DetailMixin._delete(self, request, pk)
        elif 'edit' in request.POST.keys():
            return DetailMixin._patch(self, request, pk)
        else:
            return HttpResponseBadRequest('Unknown operation!')

    def _delete(self, request, pk):
        deled_model = get_object_or_404(self.model, owner=request.user, id=pk)
        if self.from_model and getattr(deled_model, '{}_set'.format(self.from_model.__name__.lower())).count() > 0:
            return HttpResponseBadRequest('Can not delete')
        deled_model.delete()
        return redirect(self.model.get_list_url())

    def _patch(self, request, pk):
        content = get_request_content('GET', request)
        model = get_object_or_404(self.model, owner=request.user, id=pk)

        for field in self.fields:
            if field in content.keys():
                setattr(model, field, content[field])

        try:
            model.save()
            if self.relation_field in content.keys():
                getattr(model, self.relation_field).set(
                    get_models_by_id(self.to_model, content[self.relation_field], request.user))
        except ValidationError as error:
            return HttpResponseBadRequest(json.dumps({
                'type': 'validation_error',
                'content': get_validation_error_content(error)
            }))

        return redirect(model)


class CobraMetaboliteDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraMetabolite
    fields = ['cobra_id', 'name', 'formula', 'charge', 'compartment']

    from_model = CobraReaction


class CobraReactionDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraReaction
    fields = [
        'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'coefficients',
        'gene_reaction_rule'
    ]

    relation_field = 'metabolites'
    to_model = CobraMetabolite
    from_model = CobraModel


class CobraModelDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraModel
    fields = ['cobra_id', 'name', 'objective']

    relation_field = 'reactions'
    to_model = CobraReaction


class CobraModelDetailComputeView(LoginRequiredMixin, View):

    def get(self, request, pk, method):  # TODO: Actually should be post
        content = get_post_content(request)
        model = get_object_or_404(CobraModel, pk=pk, owner=request.user)

        try:
            if method == 'fba':
                # return JsonResponse(model.fba(), status=200)
                return render(request, 'cobra_wrapper/model/fba.html', context={
                    'solution': model.fba(), 'model': model
                })
            elif method == 'fva':
                fva_params = try_get_fields(
            content, ['loopless', 'fraction_of_optimum', 'pfba_factor', 'processes'])

                try:
                    if 'reaction_list' in content.keys():
                        reactions = get_models_by_id(CobraReaction, content['reaction_list'], request.user)
                        content['reaction_list'] = []
                        for reaction in reactions:
                            content['reaction_list'].append(reaction.build())
                    solution = model.fva(reaction_list=content['reaction_list'], **fva_params)
                    return render(request, 'cobra_wrapper/model/fva.html', context={
                        'solution': solution, 'model': model
                    })
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


class NewMixin:
    model = None

    to_model = None

    def get(self, request):
        return render(request, 'cobra_wrapper/{}/new.html'.format(self.model.MODEL_NAME), {
            'related_models': (self.to_model.objects.filter(owner=request.user) if self.to_model else None)
        })


class CobraMetaboliteNewView(NewMixin, View):
    model = CobraMetabolite


class CobraReactionNewView(NewMixin, View):
    model = CobraReaction

    to_model = CobraMetabolite


class CobraModelNewView(NewMixin, View):
    model = CobraModel

    to_model = CobraReaction
