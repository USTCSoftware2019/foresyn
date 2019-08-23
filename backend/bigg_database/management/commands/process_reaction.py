import json
import os

import django
from django.core.management.base import BaseCommand

from bigg_database.models import Reaction

from .progressbar import print_progressbar


def main(reaction_path):
    files_list = [os.path.join(reaction_path, file)
                  for file in os.listdir(reaction_path)
                  if not os.path.isdir(os.path.join(reaction_path, file))]
    total_len = len(files_list)
    for cnt, file in enumerate(files_list):
        print_progressbar(cnt + 1, total_len)
        with open(file, 'r', encoding='utf-8') as f:
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
                # print(reaction_string)
            except KeyError as e:
                print(e, file)
                continue

            try:
                Reaction.objects.create(bigg_id=bigg_id, name=name, reaction_string=reaction_string,
                                        pseudoreaction=pseudoreaction, database_links=database_links)
            except Exception as e:
                print(e, file)


class Command(BaseCommand):
    help = 'Generate reaction data from json'

    def add_arguments(self, parser):
        parser.add_argument('reaction_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['reaction_path'])
