import json
import os

import django
from django.core.management.base import BaseCommand

from bigg_database.models import Reaction


def main(reaction_path):
    for file in os.listdir(reaction_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(reaction_path, file), 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print(e, file)
                continue
            try:
                bigg_id = content['bigg_id']
                name = content['name'] or ''

                database_links = content['database_links']
                pseudoreaction = content['pseudoreaction']
                reaction_string = content['reaction_string']
            except KeyError as e:
                print(e, file)
                continue

            Reaction.objects.create(bigg_id=bigg_id, name=name, reaction_string=reaction_string,
                                    pseudoreaction=pseudoreaction, database_links=database_links)


class Command(BaseCommand):
    help = 'Generate reaction data from json'

    def add_arguments(self, parser):
        parser.add_argument('reaction_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['reaction_path'])
