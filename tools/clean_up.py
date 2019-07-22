# clean up database

import sys
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

if True:
    from bigg_database.models import Model, Reaction, Metabolite


def clean_model():
    Model.objects.all().delete()


def clean_meta():
    Reaction.objects.all().delete()


def clean_reaction():
    Metabolite.objects.all().delete()


def clean_all():
    clean_meta()
    clean_reaction()
    clean_model()


if len(sys.argv) == 1:
    clean_all()
elif len(sys.argv) == 2:
    if sys.argv[1] == 'meta':
        clean_meta()
    elif sys.argv[1] == 'reaction':
        clean_reaction()
    elif sys.argv[1] == 'model':
        clean_model()
    else:
        print('Usage: pass meta, reaction, model to program')

else:
    print('Usage: pass meta, reaction, model to program')
