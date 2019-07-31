import json

# from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, UpdateView
# from django.http import HttpResponseBadRequest, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
# from cobra.exceptions import OptimizationError

from .models import CobraMetabolite, CobraReaction, CobraModel
from .forms import CobraMetaboliteForm, CobraReactionForm, CobraModelForm


# def get_validation_error_content(error):
#     return {
#         field: [
#             {
#                 'code': field_error.code,
#                 'message': str(field_error.message)  # Lazy text
#             }
#             for field_error in error.error_dict[field]
#         ]
#         for field in error.error_dict.keys()
#     }


# def get_request_content(method, request):
#     info = {field: value for field, value in getattr(request, method).items()}
#     pop_metabolites_and_coefficients = False
#     for field in info.keys():
#         if field in ['reactions', 'metabolites', 'reaction_list']:
#             try:
#                 info[field] = [int(pk) for pk in getattr(request, method).getlist(field)]
#             except ValueError:
#                 pass

#         if field in ['lower_bound', 'upper_bound', 'objective_coefficient', 'pfba_factor', 'fraction_of_optimum']:
#             if info[field]:
#                 try:
#                     info[field] = float(info[field])
#                 except ValueError:
#                     pass
#             else:
#                 info[field] = {
#                     'lower_bound': 0.0,
#                     'upper_bound': None,
#                     'objective_coefficient': 0.0,
#                     'pfba_factor': None,
#                     'fraction_of_optimum': 1.0
#                 }[field]

#         if field == 'coefficients':
#             if 'metabolites' not in info.keys() or not info[field]:
#                 pop_metabolites_and_coefficients = True
#             else:
#                 try:
#                     info[field] = json.loads(info[field])
#                 except json.decoder.JSONDecodeError:
#                     pass

#         if field == 'loopless':
#             info[field] = True
#     if pop_metabolites_and_coefficients:
#         info.pop('metabolites', None)
#         info.pop('coefficients', None)
#     return info


# class ListMixin:
#     http_method_names = ['get', 'post']

#     model = None
#     form = None
#     relation_field = None
#     to_model = None

#     def post(self, request):
#         new_form = self.form(request.POST)
#         new_form.owner = request.user
#         try:
#             if self.relation_field:
#                 clean_pk_list(new_form, self.relation_field, self.to_model)
#             new_model = new_form.save()
#         except ValueError:
#             return HttpResponseBadRequest(json.dumps({
#                 'type': 'value_error',
#                 'errors': new_form.errors
#             }))
#         return redirect(new_model)

#     def get(self, request):
#         return render(request, 'cobra_wrapper/{}/list.html'.format(self.model.MODEL_NAME), context={
#             'all': self.model.objects.filter(owner=request.user)
#         })


class CobraMetaboliteListView(LoginRequiredMixin, ListMixin, View):
    model = CobraMetabolite
    form = CobraMetaboliteForm


class CobraReactionListView(LoginRequiredMixin, ListMixin, View):
    model = CobraReaction
    form = CobraReactionForm
    relation_field = 'metabolites'
    to_model = CobraMetabolite


class CobraModelListView(LoginRequiredMixin, ListMixin, View):
    model = CobraModel
    form = CobraModelForm
    relation_field = 'reactions'
    to_model = CobraReaction


# class DetailMixin:
#     http_method_names = ['get', 'post']

#     model = None
#     form = CobraMetaboliteForm
#     relation_field = None
#     to_model = None
#     from_model = None

#     def get(self, request, pk):
#         return render(request, 'cobra_wrapper/{}/detail.html'.format(self.model.MODEL_NAME), context={
#             self.model.MODEL_NAME: get_object_or_404(self.model, pk=pk, owner=request.user),
#             'related_models': (self.to_model.objects.filter(owner=request.user) if self.relation_field else None)
#         })

#     def post(self, request, pk):
#         if 'delete' in request.POST.keys():
#             return DetailMixin._delete(self, request, pk)
#         elif 'edit' in request.POST.keys():
#             return DetailMixin._patch(self, request, pk)
#         else:
#             return HttpResponseBadRequest('Unknown operation!')

#     def _delete(self, request, pk):
#         deled_model = get_object_or_404(self.model, owner=request.user, id=pk)
#         if self.from_model and getattr(deled_model, '{}_set'.format(self.from_model.__name__.lower())).count() > 0:
#             return HttpResponseBadRequest('Can not delete')
#         deled_model.delete()
#         return redirect(self.model.get_list_url())

#     def _patch(self, request, pk):
#         instance = get_object_or_404(self.model, owner=request.user, id=pk)
#         editing_form = self.form(request.POST, instance=instance)
#         editing_form.owner = request.user
#         try:
#             if self.relation_field:
#                 clean_pk_list(editing_form, self.relation_field, self.to_model)
#             edited_instance = editing_form.save()
#         except ValueError:
#             return HttpResponseBadRequest(json.dumps({
#                 'type': 'value_error',
#                 'errors': editing_form.errors
#             }))
#         return redirect(edited_instance)


class CobraMetaboliteDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraMetabolite
    form = CobraMetaboliteForm
    from_model = CobraReaction


class CobraReactionDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraReaction
    form = CobraReactionForm
    from_model = CobraModel
    relation_field = 'metabolites'
    to_model = CobraMetabolite


class CobraModelDetailView(LoginRequiredMixin, DetailMixin, View):
    model = CobraModel
    form = CobraModelForm
    relation_field = 'reactions'
    to_model = CobraReaction


# class CobraModelDetailComputeView(LoginRequiredMixin, View):

#     def get(self, request, pk, method):
#         # TODO: Shold use post to create operation and use get to seethe result
#         model = get_object_or_404(CobraModel, pk=pk, owner=request.user)

#         try:
#             if method == 'fba':
#                 return render(request, 'cobra_wrapper/model/fba.html', context={
#                     'solution': model.fba(), 'model': model
#                 })

#             elif method == 'fva':
#                 content = get_request_content('GET', request)
#                 fva_params = try_get_fields(content, ['loopless', 'fraction_of_optimum', 'pfba_factor'])

#                 try:
#                     if 'reaction_list' in content.keys():
#                         reactions = get_models_by_id(CobraReaction, content['reaction_list'], request.user)
#                         content['reaction_list'] = []
#                         for reaction in reactions:
#                             content['reaction_list'].append(reaction.build())
#                     else:
#                         content['reaction_list'] = []
#                     solution_temp = model.fva(reaction_list=content['reaction_list'], **fva_params)

#                     # TODO: validate

#                     solution = [
#                         (name, solution_temp['maximum'][name], solution_temp['minimum'][name])
#                         for name in solution_temp['maximum'].keys()
#                     ]
#                     return render(request, 'cobra_wrapper/model/fva.html', context={
#                         'solution': solution, 'model': model
#                     })
#                 except ValidationError or ValueError as error:
#                     return HttpResponseBadRequest(json.dumps({
#                         'type': 'validation_error',
#                         'content': {
#                             'reaction_list': [
#                                 {
#                                     'code': error.code,
#                                     'message': error.message
#                                 }
#                             ]
#                         }
#                     }))

#             else:
#                 return Http404()
#         except OptimizationError as error:
#             return HttpResponseBadRequest(json.dumps({'type': 'cobra_error', 'content': error.args[0]}))


# class NewMixin:
#     http_method_names = ['get']

#     model = None
#     to_model = None

#     def get(self, request):
#         return render(request, 'cobra_wrapper/{}/new.html'.format(self.model.MODEL_NAME), context={
#             'related_models': (self.to_model.objects.filter(owner=request.user) if self.to_model else None)
#         })


class CobraMetaboliteNewView(LoginRequiredMixin, NewMixin, View):
    model = CobraMetabolite


class CobraReactionNewView(LoginRequiredMixin, NewMixin, View):
    model = CobraReaction
    to_model = CobraMetabolite


class CobraModelNewView(LoginRequiredMixin, NewMixin, View):
    model = CobraModel
    to_model = CobraReaction
