
import json
import os

import django
from django.core.management.base import BaseCommand

from bigg_database.models import Gene, Model

from .progressbar import print_progressbar


def main(model_path):
    files_list = [os.path.join(model_path, file)
                  for file in os.listdir(model_path)
                  if not os.path.isdir(os.path.join(model_path, file))]
    total_len = len(files_list)

    for cnt, file in enumerate(files_list):
        print_progressbar(cnt + 1, total_len)
        with open(file, 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print(e, file)

            try:
                model_bigg_id = content['id']
                model_instance = Model.objects.get(bigg_id=model_bigg_id)
            except KeyError as e:
                print(e, file)
                continue

            for gene in content['genes']:
                gene_bigg_id = gene['id']

                gene_instance = Gene.objects.get(bigg_id=gene_bigg_id)
                gene_instance.models.add(model_instance)
                gene_instance.save()


class Command(BaseCommand):
    help = 'Link model and gene from json'

    def add_arguments(self, parser):
        parser.add_argument('model_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['model_path'])
