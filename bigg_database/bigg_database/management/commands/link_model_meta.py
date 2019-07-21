import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Metabolite, Model, ModelMetabolite


def main(model_path, meta_path):
    for file in os.listdir(model_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(model_path, file), 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                print(file)
            model_bigg_id = content['id']
            model_instance = Model.objects.get(bigg_id=model_bigg_id)
            for meta in content['metabolites']:
                meta_bigg_id = meta['id']
                meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
                ModelMetabolite.objects.create(
                    model=model_instance, metabolite=meta_instance)  # 还有organism没有加入

    for file in os.listdir(meta_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(meta_path, file), 'r', encoding='utf-8') as f:
            content = json.loads(f.read())

            meta_bigg_id_without_compartments = content['bigg_id']

            for compartment in content['compartments_in_models']:
                meta_bigg_id = meta_bigg_id_without_compartments + '_' + \
                    compartment['bigg_id']
                meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
                model_instance = Model.objects.get(
                    bigg_id=model_bigg_id)

                mm = ModelMetabolite.objects.get(
                    metabolite=meta_instance, model=model_instance)

                mm.organism = compartment['organism']
                mm.save()


class Command(BaseCommand):
    help = 'Link model and metabolite from json'

    def add_arguments(self, parser):
        parser.add_argument('model_path', type=str)
        parser.add_argument('meta_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['model_path'], kwargs['meta_path'])
