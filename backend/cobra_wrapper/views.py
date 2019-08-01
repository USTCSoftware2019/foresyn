from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# from cobra.exceptions import OptimizationError

from .models import CobraMetabolite, CobraReaction, CobraModel
from .forms import CobraModelFvaForm


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
    model = CobraMetabolite
    fields = ['owner', 'cobra_id', 'name', 'formula', 'charge', 'compartment']


class CobraReactionCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraReaction
    fields = [
        'owner', 'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'metabolites',
        'coefficients', 'gene_reaction_rule'
    ]


class CobraModelCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraModel
    fields = ['owner', 'cobra_id', 'name', 'reactions', 'objective']


class CobraMetaboliteDeleteView(LoginRequiredMixin, DeleteView):  # TODO: Check dependency
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
    fields = ['owner', 'cobra_id', 'name', 'formula', 'charge', 'compartment']

    def get_object(self):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])


class CobraReactionUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    fields = [
        'owner', 'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient', 'metabolites',
        'coefficients', 'gene_reaction_rule'
    ]

    def get_object(self):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    fields = ['owner', 'cobra_id', 'name', 'reactions', 'objective']

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelFbaDetailView(LoginRequiredMixin, SingleObjectMixin, TemplateView):
    template_name = 'cobra_wrapper/cobramodel_fba_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solution'] = self.get_object().fba()
        return context


class CobraModelFvaCreateView(LoginRequiredMixin, FormView):
    template_name = 'cobra_wrapper/cobramodel_fva_create_form.html'
    form_class = CobraModelFvaForm
    success_url = reverse_lazy('cobra_wrapper:cobramodel_fva_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_pk'] = self.request.GET['pk']
        return context


class CobraModelFvaDetailView(LoginRequiredMixin, SingleObjectMixin, TemplateView):
    template_name = 'cobra_wrapper/cobramodel_fva_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CobraModelFvaForm(request.POST)
        if form.is_valid():
            self.fva_params = form.cleaned_data
            return super().get(request, *args, **kwargs)
        else:
            return redirect(self.object)

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_obj = self.object.fva(**self.fva_params)
        context['solution'] = [
            (name, solution_obj['maximum'][name], solution_obj['minimum'][name])
            for name in solution_obj['maximum'].keys()
        ]
        return context


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
#                     solution_obj = model.fva(reaction_list=content['reaction_list'], **fva_params)

#                     # TODO: validate

#                     solution = [
#                         (name, solution_obj['maximum'][name], solution_obj['minimum'][name])
#                         for name in solution_obj['maximum'].keys()
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
