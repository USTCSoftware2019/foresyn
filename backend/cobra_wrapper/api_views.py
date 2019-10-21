import json

from django.views.generic.detail import SingleObjectMixin, View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import cobra

from . import models
from .utils import is_coenzyme


class CobraModelDetailJsonView(SingleObjectMixin, View):
    def get_object(self, queryset=None):
        return get_object_or_404(models.CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get(self, request, pk):
        self.kwargs['pk'] = pk
        json_content = cobra.io.to_json(self.get_object().build())
        return JsonResponse(json.loads(json_content))


class CobraComputationDetailJsonView(SingleObjectMixin, View):
    model_class = None
    backref_field = None

    def get_object(self, queryset=None):
        self.model_object = get_object_or_404(models.CobraModel, pk=self.kwargs['model_pk'], owner=self.request.user)
        return get_object_or_404(getattr(self.model_object, self.backref_field).all(), pk=self.kwargs['pk'])

    def get_result_dict(self):
        self.object = self.get_object()
        results = [json.loads(self.object.result)]
        results.extend([
            json.loads(fba.result)
            for fba in self.model_class.objects.filter(model=self.model_object, ok=True).exclude(pk=self.object.pk)[:1]
        ])
        return {'results': results}

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.get_result_dict())


class CobraFbaDetailJsonView(CobraComputationDetailJsonView):
    model_class = models.CobraFba
    backref_field = 'fba_list'

    def get(self, request, *arg, **kwargs):
        result_dict = self.get_result_dict()
        for result in result_dict['results']:
            result['coenzymes'] = [shadow_price for shadow_price in result['shadow_prices']
                                   if is_coenzyme(shadow_price['name'])]
        return JsonResponse(result_dict)


class CobraRgeFbaDetailJsonView(CobraComputationDetailJsonView):
    model_class = models.CobraRgeFba
    backref_field = 'rgefba_list'

    def get(self, request, *arg, **kwargs):
        result_dict = self.get_result_dict()
        for result in result_dict['results']:
            result['coenzymes'] = [shadow_price for shadow_price in result['shadow_prices']
                                   if is_coenzyme(shadow_price['name'])]
        return JsonResponse(result_dict)


class CobraFvaDetailJsonView(CobraComputationDetailJsonView):
    model_class = models.CobraFva
    backref_field = 'fva_list'
