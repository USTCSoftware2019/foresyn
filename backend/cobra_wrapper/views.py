from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from djaDeleteViewb.UpdateViews import LoginRequiredMixin
# from cobra.exceptions import OptimizationError

from .models import CobraMetabolite, CobraReaction, CobraModel


class CobraMetaboliteListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return CobraMetabolite.objects.filter(owner=self.request.user)


class CobraReactionListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return CobraReaction.objects.filter(owner=self.request.user)


class CobraModelListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return CobraModel.objects.filter(owner=self.request.user)


class CobraMetaboliteDetailView(LoginRequiredMixin, DetailView):
    def get_object(self):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])


class CobraReactionDetailView(LoginRequiredMixin, DetailView):
    def get_object(self):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelDetailView(LoginRequiredMixin, DetailView):
    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraMetaboliteCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'

    def get_object(self):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])


class CobraReactionCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'

    def get_object(self):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraMetaboliteDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobrametabolite_list')

    def get_object(self):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])


class CobraReactionDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobrareaction_list')

    def get_object(self):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobramodel_list')

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraMetaboliteUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'

    def get_object(self):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])


class CobraReactionUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'

    def get_object(self):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


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
