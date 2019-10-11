import io
import os
import subprocess

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import cobra.test

from backend.settings import BASE_DIR
from cobra_wrapper.models import CobraModel


def main():
    try:
        os.remove(os.path.join(BASE_DIR, 'db.sqlite3'))
    except FileNotFoundError:
        pass
    subprocess.run([os.path.join(BASE_DIR, 'manage.py'), 'migrate'], env=os.environ)

    user = User.objects.create_superuser('test', '', 'test123456')

    sbml_file = io.StringIO()
    # The func in libsbml can actually accept file-like object
    cobra.io.write_sbml_model(cobra.test.create_test_model(), sbml_file)
    CobraModel.objects.create(name='example_model', objective='', sbml_content=sbml_file.read(), owner=user)


class Command(BaseCommand):
    help = 'Init test database for GUI test'

    def handle(self, **kwargs):
        main()
