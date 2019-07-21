import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Reaction, Gene, ReactionGene


def main(gene_path):
    for file in os.listdir(gene_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(gene_path, file), 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print(e, file)

            gene_bigg_id = content['bigg_id']
            gene_instance = Gene.objects.get(bigg_id=gene_bigg_id)

            for reaction in content['reactions']:
                reaction_bigg_id = reaction['bigg_id']
                reaction_instance = Reaction.objects.get(
                    bigg_id=reaction_bigg_id)
                ReactionGene.objects.create(
                    reaction=reaction_instance, gene=gene_instance,
                    gene_reaction_rule=reaction['gene_reaction_rule'])


class Command(BaseCommand):
    help = 'Link reaction and gene from json'

    def add_arguments(self, parser):
        parser.add_argument('gene_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['gene_path'])