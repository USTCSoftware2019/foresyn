from django.contrib import admin

from .models import (CobraMetabolite, CobraReaction, CobraModel, CobraFba, CobraFva, CobraMetaboliteChange,
                     CobraReactionChange, CobraModelChange)

admin.site.register(CobraMetabolite)
admin.site.register(CobraReaction)
admin.site.register(CobraModel)
admin.site.register(CobraFba)
admin.site.register(CobraFva)
admin.site.register(CobraMetaboliteChange)
admin.site.register(CobraReactionChange)
admin.site.register(CobraModelChange)
