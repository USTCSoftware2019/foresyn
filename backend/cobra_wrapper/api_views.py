import json
from typing import Dict, Union

from django.views.generic.detail import SingleObjectMixin, View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import cobra

from . import models


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

    COENZYMES = ['NADN', 'NAD', 'NADPH', 'NADP', 'ATP', 'FMN', 'FMNH2', 'FAD', 'FADH2']

    # TODO(myl7): More grace way to implement
    def get_result_dict(self):
        result_dict = super().get_result_dict()
        got_compared = len(result_dict['results']) > 1

        def key_func(x: Dict[str, Union[str, float]]) -> str:
            return x['name']

        result_dict['results'][0]['fluxes'].sort(key=key_func)
        result_dict['results'][0]['reduced_costs'].sort(key=key_func)
        result_dict['results'][0]['shadow_prices'].sort(key=key_func)
        if got_compared:
            result_dict['results'][1]['fluxes'].sort(key=key_func)
            result_dict['results'][1]['reduced_costs'].sort(key=key_func)
            result_dict['results'][1]['shadow_prices'].sort(key=key_func)

        flux_name_list = [flux['name'] for flux in result_dict['results'][0]['fluxes']]
        shadow_price_name_list = [shadow_price['name'] for shadow_price in result_dict['results'][0]['shadow_prices']]
        new_result_dict = result_dict.copy()
        flux_pop_names = []
        shadow_price_pop_names = []

        for i, name in enumerate(flux_name_list):
            if (not got_compared
                and result_dict['results'][0]['fluxes'][i]['value'] < 0.001
                and result_dict['results'][0]['reduced_costs'][i]['value'] < 0.001) or \
                    (got_compared
                     and result_dict['results'][0]['fluxes'][i]['value'] < 0.001
                     and result_dict['results'][0]['reduced_costs'][i]['value'] < 0.001
                     and result_dict['results'][1]['fluxes'][i]['value'] < 0.001
                     and result_dict['results'][1]['reduced_costs'][i]['value'] < 0.001):
                flux_pop_names.append(i)

        for i, name in enumerate(shadow_price_name_list):
            if (not got_compared
                and result_dict['results'][0]['shadow_prices'][i]['value'] < 0.001) or \
                    (got_compared
                     and result_dict['results'][0]['shadow_prices'][i]['value'] < 0.001
                     and result_dict['results'][1]['shadow_prices'][i]['value'] < 0.001):
                shadow_price_pop_names.append(i)

        flux_pop_names.reverse()
        shadow_price_pop_names.reverse()

        for i in flux_pop_names:
            new_result_dict['results'][0]['fluxes'].pop(i)
            new_result_dict['results'][0]['reduced_costs'].pop(i)
            if got_compared:
                new_result_dict['results'][1]['fluxes'].pop(i)
                new_result_dict['results'][1]['reduced_costs'].pop(i)

        for i in shadow_price_pop_names:
            new_result_dict['results'][0]['shadow_prices'].pop(i)
            if got_compared:
                new_result_dict['results'][1]['shadow_prices'].pop(i)

        return new_result_dict

    def get(self, request, *arg, **kwargs):
        result_dict = self.get_result_dict()
        for result in result_dict['results']:
            result['coenzymes'] = [flux for flux in result['fluxes'] if flux['name'] in self.COENZYMES]
        return JsonResponse(result_dict)


class CobraRgeFbaDetailJsonView(CobraComputationDetailJsonView):
    model_class = models.CobraRgeFba
    backref_field = 'rgefba_list'


class CobraFvaDetailJsonView(CobraComputationDetailJsonView):
    model_class = models.CobraFva
    backref_field = 'fva_list'
