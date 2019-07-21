import json
import os

import django
from django.core.management.base import BaseCommand

from bigg_database.models import Metabolite, Reaction, ReactionMetabolite


def main(reaction_path):
    for file in os.listdir(reaction_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(reaction_path, file), 'r', encoding='utf-8') as f:
            content = json.loads(f.read())

            reaction_bigg_id = content['bigg_id']
            reaction_instance = Reaction.objects.get(bigg_id=reaction_bigg_id)
            for meta in content['metabolites']:
                meta_bigg_id = meta['bigg_id'] + \
                    '_' + meta['compartment_bigg_id']
                meta_stoichiometry = meta['stoichiometry']
                meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
                ReactionMetabolite.objects.create(
                    reaction=model_instance, metabolite=meta_instance, stoichiometry=meta_stoichiometry)


class Command(BaseCommand):
    help = 'Link reaction and metabolite from json'

    def add_arguments(self, parser):
        parser.add_argument('reaction_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['reaction_path'])
