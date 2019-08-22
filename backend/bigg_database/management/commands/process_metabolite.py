
import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Metabolite


def main(meta_path):
    for file in os.listdir(meta_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(meta_path, file), 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print(e, file)
                continue
            try:
                bigg_id_without_compartment = content['bigg_id']
                name = content['name'] or ''
                formulae = content['formulae']
            except KeyError as e:
                print(e, file)
                continue
            try:
                charges = content['charges'][0]
            # except IndexError as e:
            except IndexError:
                charges = None
            database_links = content['database_links']

            for compartment_id in set([compartment['bigg_id'] for compartment in content['compartments_in_models']]):
                bigg_id = bigg_id_without_compartment + \
                    '_' + compartment_id
                try:
                    Metabolite.objects.create(
                        bigg_id=bigg_id, name=name, formulae=formulae,
                        charges=charges, database_links=database_links)
                except Exception as e:
                    print(e)


class Command(BaseCommand):
    help = 'Generate model data from json'

    def add_arguments(self, parser):
        parser.add_argument('meta_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['meta_path'])
