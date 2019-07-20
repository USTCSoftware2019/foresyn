# clean up database

import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

if True:
    from bigg_database.models import Model, Reaction, Metabolite

Model.objects.all().delete()
Reaction.objects.all().delete()
Metabolite.objects.all().delete()
