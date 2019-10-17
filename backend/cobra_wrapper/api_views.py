import json

from django.views.generic.detail import SingleObjectMixin, View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import cobra

from .models import CobraModel, CobraFba, CobraFva


class CobraModelDetailJsonView(SingleObjectMixin, View):
    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get(self, request, pk):
        self.kwargs['pk'] = pk
        json_content = cobra.io.to_json(self.get_object().build())
        return JsonResponse(json.loads(json_content))


class CobraComputationDetailJsonView(SingleObjectMixin, View):
    model_class = None
    backref_field = None

    def get_object(self, queryset=None):
        self.model_object = get_object_or_404(CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(getattr(self.model_object, self.backref_field).all(), pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        results = [json.loads(self.object.result)]
        results.extend([
            json.loads(fba.result)
            for fba in self.model_class.objects.filter(model=self.model_object, ok=True).exclude(pk=self.object.pk)[:1]
        ])
        return JsonResponse({'results': results})


class CobraFbaDetailJsonView(CobraComputationDetailJsonView):
    model_class = CobraFba
    backref_field = 'fba_list'


class CobraFvaDetailJsonView(CobraComputationDetailJsonView):
    model_class = CobraFva
    backref_field = 'fva_list'
