from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_celery_results.models import TaskResult

from .models import CobraMetabolite, CobraReaction, CobraModel, CobraFba, CobraFva
from .forms import CobraReactionForm, CobraModelForm, CobraFvaForm


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
    def get_object(self, queryset=None):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])


class CobraReactionDetailView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelDetailView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
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

    def get_form(self, form_class=None):
        return CobraReactionForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraModelCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraModel  # TODO(myl7): Is model required ?

    def get_form(self, form_class=None):
        return CobraModelForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraMetaboliteDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobrametabolite_list')

    def get_object(self, queryset=None):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deletable'] = (self.object.cobrareaction_set.count() == 0)
        return context


class CobraReactionDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobrareaction_list')

    def get_object(self, queryset=None):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deletable'] = (self.object.cobramodel_set.count() == 0)
        return context


class CobraModelDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobramodel_list')

    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraMetaboliteUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    fields = ['cobra_id', 'name', 'formula', 'charge', 'compartment']

    def get_object(self, queryset=None):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraReactionUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'

    def get_object(self, queryset=None):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        return CobraReactionForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CobraModelUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'

    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        return CobraModelForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ModelPkMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context


class CobraFbaListView(LoginRequiredMixin, ModelPkMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.cobrafba_set.all()


class CobraFbaDetailView(LoginRequiredMixin, ModelPkMixin, DetailView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafba_set.all(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['result'] = TaskResult.objects.get(task_id=self.object.task_id)
        except TaskResult.DoesNotExist:
            context['result'] = None
        return context


class CobraFbaCreateView(LoginRequiredMixin, ModelPkMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraFba
    fields = []

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.model = self.object
        # form.instance.result_id  # TODO(myl7): Celery
        return super().form_valid(form)


class CobraFbaDeleteView(LoginRequiredMixin, ModelPkMixin, DeleteView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafba_set.all(), pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFvaListView(LoginRequiredMixin, ModelPkMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.cobrafva_set.all()


class CobraFvaDetailView(LoginRequiredMixin, ModelPkMixin, DetailView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafva_set.all(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['result'] = TaskResult.objects.get(task_id=self.object.task_id)
        except TaskResult.DoesNotExist:
            context['result'] = None
        return context


class CobraFvaCreateView(LoginRequiredMixin, ModelPkMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraFva

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return CobraFvaForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.model = self.object
        # form.instance.result_id  # TODO(myl7): Celery
        return super().form_valid(form)


class CobraFvaDeleteView(LoginRequiredMixin, ModelPkMixin, DeleteView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafva_set.all(), pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafva_list', kwargs={'model_pk': self.kwargs['model_pk']})
