import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Metabolite, Model, ModelMetabolite
from .progressbar import print_progressbar


def main(meta_path):
    files_list = [os.path.join(meta_path, file)
                  for file in os.listdir(meta_path)
                  if not os.path.isdir(os.path.join(meta_path, file))]

    file_cnt = len(files_list)
    print_progressbar(0, file_cnt)
    for count, file in enumerate(files_list):
        print_progressbar(count + 1, file_cnt)
        with open(file, 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print(e, file)

            try:
                meta_bigg_id_without_compartments = content['bigg_id']
            except KeyError as e:
                print(e, file)
                continue

            for compartment in content['compartments_in_models']:
                meta_bigg_id = meta_bigg_id_without_compartments + '_' + \
                    compartment['bigg_id']
                meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
                model_instance = Model.objects.get(
                    bigg_id=compartment['model_bigg_id'])

                try:
                    mm = ModelMetabolite.objects.create(
                        metabolite=meta_instance, model=model_instance)

                    mm.organism = compartment['organism']
                    mm.save()
                except Exception as e:
                    print(e, meta_bigg_id, compartment['model_bigg_id'])


class Command(BaseCommand):
    help = 'Link model and metabolite from json'

    def add_arguments(self, parser):
        parser.add_argument('meta_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['meta_path'])
