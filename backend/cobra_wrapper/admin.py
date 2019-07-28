from django.contrib import admin

from .models import CobraMetabolite, CobraReaction, CobraModel

admin.site.register(CobraMetabolite)
admin.site.register(CobraReaction)
admin.site.register(CobraModel)
