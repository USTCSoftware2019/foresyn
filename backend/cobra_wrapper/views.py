import json

from django.shortcuts import get_object_or_404, reverse, Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
import cobra

from .models import CobraModel, CobraFba, CobraFva
from .forms import CobraModelCreateForm, cobra_model_update_forms, CobraFvaForm

from backend.celery import app


class CobraModelListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return CobraModel.objects.filter(owner=self.request.user)


class CobraModelDetailView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data['cobra_model'] = self.object.build()
        return context_data


class CobraModelCreateView(LoginRequiredMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraModel
    form_class = CobraModelCreateForm

    def form_valid(self, form: CobraModelCreateForm):
        form.save(self.request.user)
        return super().form_valid(form)


class CobraModelDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('cobra_wrapper:cobramodel_list')

    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelUpdateView(LoginRequiredMixin, SingleObjectMixin, SingleObjectTemplateResponseMixin, FormView):
    template_name_suffix = '_update_form'

    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_forms(self):
        return [form() for form in cobra_model_update_forms.values()]

    def get_form_class(self):
        change_type = self.request.POST.get('change_type', None)
        try:
            return cobra_model_update_forms[change_type]
        except KeyError:
            if self.request.method == 'GET':
                return None
            else:
                raise Http404()

    def get_form(self, form_class=None):
        self.form_class = self.get_form_class()
        if self.form_class is None:
            return None
        else:
            return super().get_form()

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context_data = super().get_context_data(**kwargs)
        context_data['forms'] = self.get_forms()
        return context_data

    def form_valid(self, form):
        self.object = self.get_object()
        form.save(self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cobra_wrapper:cobramodel_detail', kwargs={'pk': self.object.pk})


class TemplateAddModelPkMixin:
    def get_context_data(self: TemplateView, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context


class TemplateAddResultMixin:
    def get_context_data(self: DetailView, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = json.loads(self.object.result) if self.object.result else None
        return context


class CobraFbaListView(LoginRequiredMixin, TemplateAddModelPkMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.cobrafba_set.all()


class CobraFbaDetailView(LoginRequiredMixin, TemplateAddModelPkMixin, TemplateAddResultMixin, DetailView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafba_set.all(), pk=self.kwargs['pk'])


# TODO(myl7): New creation view
class CobraFbaCreateView(LoginRequiredMixin, TemplateAddModelPkMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraFba
    fields = ['desc']

    def form_valid(self, form: Form):
        model_object = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        form.instance.model = model_object
        response = super().form_valid(form)
        cobra_model = model_object.build()
        delete_genes = cobra_model.genes.split(',')  # TODO(lbc12345):add delete
        result = app.send_task(
            'cobra_computation.tasks.cobra_fba',
            args=[self.object.pk, cobra.io.to_json(cobra_model), delete_genes],  # TODO(lbc12345): add delete
            kwargs={},
            queue='cobra_feeds',
            routing_key='cobra_feed.fba'
        )
        self.object.task_id = result.id
        self.object.save()
        return response

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFbaDeleteView(LoginRequiredMixin, TemplateAddModelPkMixin, DeleteView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafba_set.all(), pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFvaListView(LoginRequiredMixin, TemplateAddModelPkMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.cobrafva_set.all()


class CobraFvaDetailView(LoginRequiredMixin, TemplateAddModelPkMixin, TemplateAddResultMixin, DetailView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafva_set.all(), pk=self.kwargs['pk'])


# TODO(myl7): New creation view
class CobraFvaCreateView(LoginRequiredMixin, TemplateAddModelPkMixin, CreateView):
    template_name_suffix = '_create_form'
    model = CobraFva

    def get_form(self, form_class=None):
        return CobraFvaForm(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form: Form):
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

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafva_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFvaDeleteView(LoginRequiredMixin, TemplateAddModelPkMixin, DeleteView):
    def get_object(self, queryset=None):
        model = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.cobrafva_set.all(), pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafva_list', kwargs={'model_pk': self.kwargs['model_pk']})
