import json

from django.views.generic.detail import SingleObjectMixin, View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import cobra

from .models import CobraModel


class CobraModelDetailJsonView(SingleObjectMixin, View):
    def get_object(self, queryset=None):
        return get_object_or_404(CobraModel, owner=self.request.user, pk=self.kwargs['pk'])

    def get(self, request, pk):
        self.kwargs['pk'] = pk
        json_content = cobra.io.to_json(self.get_object().build())
        return JsonResponse(json.loads(json_content))
