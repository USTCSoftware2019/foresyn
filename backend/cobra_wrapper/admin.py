from django.contrib import admin

from .models import CobraModel, CobraFba, CobraFva, CobraModelChange

admin.site.register(CobraModel)
admin.site.register(CobraFba)
admin.site.register(CobraFva)
admin.site.register(CobraModelChange)
