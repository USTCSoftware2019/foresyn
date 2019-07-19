import json

from django.views import View
from django.contrib.auth import authenticate, login
from django.http import JsonResponse


class AccountsView(View):
    def post(self, request):
        user = authenticate(**json.loads(request.body))
        if user:
            login(request, user)
            return JsonResponse({}, status=201)
        else:
            return JsonResponse({
                'code': 100001,
                'message': 'Invalid credentials'
            }, status=400)
