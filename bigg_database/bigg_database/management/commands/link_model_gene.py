
import json
import os

import django
from django.core.management.base import BaseCommand

from bigg_database.models import Gene, Model


def main(model_path):
    for file in os.listdir(model_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(model_path, file), 'r', encoding='utf-8') as f:
            content = json.loads(f.read())

            model_bigg_id = content['id']
            model_instance = Model.objects.get(bigg_id=model_bigg_id)

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
