from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# from cobra.exceptions import OptimizationError

from .models import CobraMetabolite, CobraReaction, CobraModel
from .forms import CobraReactionForm, CobraModelFvaForm


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
    fields = ['cobra_id', 'name', 'formula', 'charge', 'compartment']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraReactionCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraReaction
    form_class = CobraReactionForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraModelCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraModel
    fields = ['cobra_id', 'name', 'reactions', 'objective']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraMetaboliteDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobrametabolite_list')

    def get_object(self):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deletable'] = self.object.cobrareaction_set.count() == 0
        return context


class CobraReactionDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobrareaction_list')

    def get_object(self):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deletable'] = self.object.cobramodel_set.count() == 0
        return context


class CobraModelDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobramodel_list')

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraMetaboliteUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    fields = ['cobra_id', 'name', 'formula', 'charge', 'compartment']

    def get_object(self):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraReactionUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = CobraReactionForm

    def get_object(self):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraModelUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    fields = ['cobra_id', 'name', 'reactions', 'objective']

    def get_object(self):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


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

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_pk'] = self.kwargs['pk']
        return context


class CobraModelFvaDetailView(LoginRequiredMixin, SingleObjectMixin, TemplateView):
    template_name = 'cobra_wrapper/cobramodel_fva_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CobraModelFvaForm(self.request.user, request.GET)
        form.is_valid()
        self.fva_params = form.cleaned_data
        return super().get(request, *args, **kwargs)

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
