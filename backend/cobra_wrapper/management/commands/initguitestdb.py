import os
import subprocess

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import cobra.test

from backend.settings import BASE_DIR
from cobra_wrapper.models import CobraModel
from cobra_wrapper.utils import dump_sbml


def main():
    try:
        os.remove(os.path.join(BASE_DIR, 'db.sqlite3'))
    except FileNotFoundError:
        pass
    subprocess.run([os.path.join(BASE_DIR, 'manage.py'), 'migrate'], env=os.environ)
    user = User.objects.create_superuser('test', '', 'test123456')
    cobra_model = cobra.test.create_test_model()
    model = CobraModel.objects.create(name='example', sbml_content=dump_sbml(cobra_model), owner=user)
    model.cache(cobra_model)


class Command(BaseCommand):
    help = 'Init test database for GUI test'

    def handle(self, **kwargs):
        main()
