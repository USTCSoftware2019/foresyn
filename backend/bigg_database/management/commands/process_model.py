import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Model
from .progressbar import print_progressbar


def main(model_path):
    files_list = [os.path.join(model_path, file)
                  for file in os.listdir(model_path)
                  if not os.path.isdir(os.path.join(model_path, file))
                  ]
    total_len = len(files_list)
    for cnt, file in enumerate(files_list):
        print_progressbar(cnt + 1, total_len)
        with open(file, 'r', encoding='utf-8') as f:
            content = json.loads(f.read())

            bigg_id = content['id']
            compartments = [key for key in content['compartments'].keys()]

            version = content['version']
            Model.objects.create(
                bigg_id=bigg_id, compartments=compartments, version=version)


class Command(BaseCommand):
    help = 'Generate model data from json'

    def add_arguments(self, parser):
        parser.add_argument('model_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['model_path'])
