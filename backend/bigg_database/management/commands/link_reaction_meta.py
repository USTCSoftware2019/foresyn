import json
import os

import django
from django.core.management.base import BaseCommand

from bigg_database.models import Metabolite, Reaction, ReactionMetabolite

from .progressbar import print_progressbar


def main(reaction_path):
    files_list = [os.path.join(reaction_path, file)
                  for file in os.listdir(reaction_path)
                  if not os.path.isdir(os.path.join(reaction_path, file))
                  ]
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
                reaction_bigg_id = content['bigg_id']
            except KeyError as e:
                print(e, file)
                continue

            reaction_instance = Reaction.objects.get(bigg_id=reaction_bigg_id)
            for meta in content['metabolites']:
                meta_bigg_id = meta['bigg_id'] + \
                    '_' + meta['compartment_bigg_id']
                meta_stoichiometry = meta['stoichiometry']
                meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
                ReactionMetabolite.objects.create(
                    reaction=reaction_instance, metabolite=meta_instance, stoichiometry=meta_stoichiometry)


class Command(BaseCommand):
    help = 'Link reaction and metabolite from json'

    def add_arguments(self, parser):
        parser.add_argument('reaction_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['reaction_path'])
