import os
import subprocess

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from backend.settings import BASE_DIR
from cobra_wrapper.models import CobraModel


def main():
    try:
        os.remove(os.path.join(BASE_DIR, 'db.sqlite3'))
    except FileNotFoundError:
        pass
    subprocess.run([os.path.join(BASE_DIR, 'manage.py'), 'migrate'], env=os.environ)

    user = User.objects.create_superuser('test', '', 'test123456')

    # TODO(myl7): Create model


class Command(BaseCommand):
    help = 'Init test database for GUI test'

    def handle(self, **kwargs):
        main()
