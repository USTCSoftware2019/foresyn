import json

from django.shortcuts import get_object_or_404, reverse, Http404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, View
from django.views.generic.edit import DeletionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.utils import timezone

from . import models, forms
from .utils import load_comma_separated_str

from backend.celery import app
from search.internal_api import search_biobricks


class CobraModelListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return models.CobraModel.objects.filter(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(object_list=object_list, **kwargs)
        context_data['form'] = forms.CobraModelCreateForm()
        return context_data


class CobraModelDetailView(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(models.CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_update_forms(self):
        return [form() for form in forms.cobra_model_update_forms.values()]

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data['forms'] = self.get_update_forms()
        context_data['reactions'] = json.loads(self.object.reactions)
        context_data['metabolites'] = json.loads(self.object.metabolites)
        context_data['genes'] = json.loads(self.object.genes)
        context_data['latest_changes'] = models.CobraModelChange.objects.filter(model=self.object)[:10]
        context_data['change_line_len'] = context_data['latest_changes'].count() * 95

        keywords = set()
        reaction_dict_list = [
            json.loads(change.reaction_info)
            for change in models.CobraModelChange.objects.filter(
                model=self.object, change_type__in=['add_reaction', 'del_reaction'])[:10]
        ]
        for reaction_dict in reaction_dict_list:
            for reaction in reaction_dict['reactions']:
                keywords.add(reaction['name'])
                keywords.update(reaction['metabolites'])
                keywords.update(reaction['genes'])
        context_data['biobricks'] = search_biobricks(*keywords)

        return context_data


class CobraModelMapView(LoginRequiredMixin, TemplateView):
    template_name = 'cobra_wrapper/cobramodel_map.html'


class CobraModelCreateView(LoginRequiredMixin, FormView):
    http_method_names = ['post']
    template_name = 'cobra_wrapper/cobramodel_list.html'
    form_class = forms.CobraModelCreateForm

    def form_valid(self, form: forms.CobraModelCreateForm):
        self.new_model = form.save(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return self.new_model.get_absolute_url()


class CobraModelDeleteView(LoginRequiredMixin, DeletionMixin, View):
    http_method_names = ['post']
    success_url = reverse_lazy('cobra_wrapper:cobramodel_list')

    def get_object(self):
        return get_object_or_404(models.CobraModel, owner=self.request.user, pk=self.kwargs['pk'])


class CobraModelUpdateView(LoginRequiredMixin, FormView):
    http_method_names = ['post']
    template_name_suffix = '_update_form'

    def get_object(self):
        return get_object_or_404(models.CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get_forms(self):
        return [form() for form in forms.cobra_model_update_forms.values()]

    def get_form_class(self):
        change_type = self.request.POST.get('change_type', None)
        try:
            return forms.cobra_model_update_forms[change_type]
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
            form = super().get_form()
            self.object = self.get_object()
            form.model_object = self.object
            return form

    def form_valid(self, form):
        form.save(self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cobra_wrapper:cobramodel_detail', kwargs={'pk': self.object.pk})


# class CobraModelChangeRestoreView(FormView):
#     http_method_names = ['post']
#     form_class = forms.CobraModelChangeRestoreForm
#
#     def get_object(self):
#         model_object = get_object_or_404(models.CobraModel, pk=self.kwargs['pk'], owner=self.request.user)
#         return get_object_or_404(models.CobraModelChange, pk=self.kwargs['change_pk'], model=model_object)
#
#     def form_valid(self, form: forms.CobraModelChangeRestoreForm):
#         change = self.get_object()
#         self.new_model = change.restore(name=form.cleaned_data['name'], desc=form.cleaned_data['desc'])
#
#     def get_success_url(self):
#         return reverse(self.new_model)


class CobraModelChangeRestoreView(View):
    http_method_names = ['post']

    def get_object(self):
        model_object = get_object_or_404(models.CobraModel, pk=self.kwargs['pk'], owner=self.request.user)
        return get_object_or_404(models.CobraModelChange, pk=self.kwargs['change_pk'], model=model_object)

    def post(self, request, *args, **kwargs):
        change = self.get_object()
        new_model = change.restore('Restored from {}'.format(change.model.name),
                                   timezone.now().strftime('%Y-%m-%d %H:%M:%S'))
        return redirect(new_model)


class TemplateAddModelPkMixin:
    def get_context_data(self: TemplateView, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_pk'] = self.kwargs['model_pk']
        return context


class InsertModelForFormMixin:
    def get_form(self: FormView, form_class=None):
        self.model_object = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        form = super().get_form()
        form.model_object = self.model_object
        return form


class CobraFbaListView(LoginRequiredMixin, TemplateAddModelPkMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.fba_list.all()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = forms.CobraFbaForm()
        return context_data


class CobraFbaDetailView(LoginRequiredMixin, TemplateAddModelPkMixin, DetailView):
    def get_object(self, queryset=None):
        self.model_object = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(self.model_object.fba_list.all(), pk=self.kwargs['pk'])


class CobraFbaCreateView(LoginRequiredMixin, InsertModelForFormMixin, TemplateAddModelPkMixin, CreateView):
    http_method_names = ['post']
    template_name = 'cobra_wrapper/cobrafba_list.html'
    model = models.CobraFba
    form_class = forms.CobraFbaForm

    def form_valid(self, form: Form):
        form.instance.model = self.model_object
        response = super().form_valid(form)
        result = app.send_task(
            'cobra_computation.tasks.cobra_fba',
            kwargs={
                'pk': self.object.pk,
                'model_sbml': self.model_object.sbml_content,
                'deleted_genes': load_comma_separated_str(form.cleaned_data['deleted_genes']),
                'computation_type': 'normal',
            },
            queue='cobra_feeds',
            routing_key='cobra_feed.fba',
        )
        self.object.task_id = result.id
        self.object.save()
        return response

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFbaDeleteView(LoginRequiredMixin, DeletionMixin, View):
    http_method_names = ['post']

    def get_object(self):
        model = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.fba_list.all(), pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraRgeFbaListView(LoginRequiredMixin, TemplateAddModelPkMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.rgefba_list.all()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = forms.CobraRgeFbaForm()
        return context_data


class CobraRgeFbaDetailView(LoginRequiredMixin, TemplateAddModelPkMixin, DetailView):
    def get_object(self, queryset=None):
        self.model_object = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(self.model_object.rgefba_list.all(), pk=self.kwargs['pk'])


class CobraRgeFbaCreateView(LoginRequiredMixin, InsertModelForFormMixin, TemplateAddModelPkMixin, CreateView):
    http_method_names = ['post']
    template_name = 'cobra_wrapper/cobrargefba_list.html'
    model = models.CobraRgeFba
    form_class = forms.CobraRgeFbaForm

    def form_valid(self, form: Form):
        form.instance.model = self.model_object
        response = super().form_valid(form)
        result = app.send_task(
            'cobra_computation.tasks.cobra_fba',
            kwargs={
                'pk': self.object.pk,
                'model_sbml': self.model_object.sbml_content,
                'deleted_genes': load_comma_separated_str(form.cleaned_data['deleted_genes']),
                'computation_type': 'regular',
            },
            queue='cobra_feeds',
            routing_key='cobra_feed.rge_fba',
        )
        self.object.task_id = result.id
        self.object.save()
        return response

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrargefba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraRgeFbaDeleteView(LoginRequiredMixin, DeletionMixin, View):
    http_method_names = ['post']

    def get_object(self):
        model = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.rgefba_list.all(), pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrargefba_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFvaListView(LoginRequiredMixin, TemplateAddModelPkMixin, ListView):
    def get_queryset(self):
        model = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return model.fva_list.all()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = forms.CobraFvaForm()
        return context_data


class CobraFvaDetailView(LoginRequiredMixin, TemplateAddModelPkMixin, DetailView):
    def get_object(self, queryset=None):
        self.model_object = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(self.model_object.fva_list.all(), pk=self.kwargs['pk'])


class CobraFvaCreateView(LoginRequiredMixin, InsertModelForFormMixin, TemplateAddModelPkMixin, CreateView):
    http_method_names = ['post']
    template_name = 'cobra_wrapper/cobrafva_list.html'
    model = models.CobraFva
    form_class = forms.CobraFvaForm

    def form_valid(self, form: Form):
        form.instance.model = self.model_object
        response = super().form_valid(form)
        result = app.send_task(
            'cobra_computation.tasks.cobra_fva',
            kwargs={
                'pk': self.object.pk,
                'model_sbml': self.model_object.sbml_content,
                'reaction_list': load_comma_separated_str(form.cleaned_data['reaction_list']),
                'loopless': form.cleaned_data['loopless'],
                'fraction_of_optimum': form.cleaned_data['fraction_of_optimum'],
                'pfba_factor': form.cleaned_data['pfba_factor'],
                'deleted_genes': load_comma_separated_str(form.cleaned_data['deleted_genes']),
            },
            queue='cobra_feeds',
            routing_key='cobra_feed.fva',
        )
        self.object.task_id = result.id
        self.object.save()
        return response

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafva_list', kwargs={'model_pk': self.kwargs['model_pk']})


class CobraFvaDeleteView(LoginRequiredMixin, DeletionMixin, View):
    http_method_names = ['post']

    def get_object(self):
        model = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(model.fva_list.all(), pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('cobra_wrapper:cobrafva_list', kwargs={'model_pk': self.kwargs['model_pk']})
