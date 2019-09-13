import json

from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import cobra

from .models import (CobraMetabolite, CobraReaction, CobraModel, CobraFba, CobraFva, CobraMetaboliteChange,
                     CobraReactionChange, CobraModelChange)
from .forms import CobraReactionForm, CobraModelForm, CobraFvaForm

from backend.celery import app


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
        response = super().form_valid(form)
        CobraMetaboliteChange.objects.create(fields='', previous_values='', values='', instance=form.instance)
        return response


class CobraReactionCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraReaction

    def get_form(self, form_class=None):
        return CobraReactionForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        CobraReactionChange.objects.create(fields='', previous_values='', values='', instance=form.instance)
        return response


class CobraModelCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraModel

    def get_form(self, form_class=None):
        return CobraModelForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        CobraModelChange.objects.create(fields='', previous_values='', values='', instance=form.instance)
        return response


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.changed_field_pre_values = ''

    def get_object(self, queryset=None):
        return get_object_or_404(CobraMetabolite, owner=self.request.user, pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.changed_field_pre_values = ', '.join([str(getattr(form.instance, field)) for field in form.changed_data])
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        CobraMetaboliteChange.objects.create(
            fields=', '.join(form.changed_data),
            previous_values=self.changed_field_pre_values,
            values=', '.join([str(form.cleaned_data[field]) for field in form.changed_data]),
            instance=form.instance)
        return response


class CobraReactionUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.changed_field_pre_values = ''

    def get_object(self, queryset=None):
        return get_object_or_404(CobraReaction, owner=self.request.user, pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        form = CobraReactionForm(self.request.user, **self.get_form_kwargs())
        self.changed_field_pre_values = ', '.join([str(getattr(form.instance, field)) for field in form.changed_data])
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        CobraReactionChange.objects.create(
            fields=', '.join(form.changed_data),
            previous_values=self.changed_field_pre_values,
            values=', '.join([str(form.cleaned_data[field]) for field in form.changed_data]),
            instance=form.instance)
        return response


class CobraModelUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.changed_field_pre_values = ''

    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_form(self, form_class=None):
        form = CobraModelForm(self.request.user, **self.get_form_kwargs())
        self.changed_field_pre_values = ', '.join([str(getattr(form.instance, field)) for field in form.changed_data])
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        CobraModelChange.objects.create(
            fields=', '.join(form.changed_data),
            previous_values=self.changed_field_pre_values,
            values=', '.join([str(form.cleaned_data[field]) for field in form.changed_data]),
            instance=form.instance)
        return response


class CobraFbaListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.cobrafba_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context


class CobraFbaDetailView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafba_set.all(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        context['result'] = json.loads(self.object.result) if self.object.result else None
        return context


class CobraFbaCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraFba
    fields = ['desc']

    def form_valid(self, form):
        model_object = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        form.instance.model = model_object
        response = super().form_valid(form)
        cobra_model = model_object.build()
        result = app.send_task(
            'cobra_computation.tasks.cobra_fba',
            args=[self.object.pk, cobra.io.to_json(cobra_model)],
            kwargs={},
            queue='cobra_feeds',
            routing_key='cobra_feed.fba'
        )
        self.object.task_id = result.id
        self.object.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFbaDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafba_set.all(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFvaListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.cobrafva_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context


class CobraFvaDetailView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafva_set.all(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        context['result'] = json.loads(self.object.result) if self.object.result else None
        return context


class CobraFvaCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraFva

    def get_form(self, form_class=None):
        return CobraFvaForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        model_object = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        form.instance.model = model_object
        cobra_fva_kwargs = {
            'reaction_list': (
                [reaction.cobra_id for reaction in form.cleaned_data['reaction_list']]
                if form.cleaned_data['reaction_list'] else None
            ),
            'loopless': form.cleaned_data['loopless'],
            'fraction_of_optimum': form.cleaned_data['fraction_of_optimum'],
            'pfba_factor': form.cleaned_data['pfba_factor']
        }
        response = super().form_valid(form)
        cobra_model = model_object.build()
        result = app.send_task(
            'cobra_computation.tasks.cobra_fva',
            args=[self.object.pk, cobra.io.to_json(cobra_model)],
            kwargs=cobra_fva_kwargs,
            queue='cobra_feeds',
            routing_key='cobra_feed.fva'
        )
        self.object.task_id = result.id
        self.object.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafva_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFvaDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafva_set.all(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafva_list', kwargs={'model_pk': self.kwargs['model_pk']})
