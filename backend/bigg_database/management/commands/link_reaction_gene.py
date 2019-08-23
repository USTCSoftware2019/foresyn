import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Gene, Reaction, ReactionGene

from .progressbar import print_progressbar


def main(gene_path):
    files_list = [os.path.join(gene_path, file)
                  for file in os.listdir(gene_path)
                  if not os.path.isdir(os.path.join(gene_path, file))
                  ]
    total_len = len(files_list)

    for cnt, file in enumerate(files_list):
        print_progressbar(cnt + 1, total_len)
        with open(file, 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print(e, file)

            try:
                gene_bigg_id = content['bigg_id']
            except KeyError as e:
                print(e, file)

            gene_instance = Gene.objects.get(bigg_id=gene_bigg_id)

            for reaction in content['reactions']:
                reaction_bigg_id = reaction['bigg_id']
                reaction_instance = Reaction.objects.get(
                    bigg_id=reaction_bigg_id)
                try:
                    ReactionGene.objects.create(
                        reaction=reaction_instance, gene=gene_instance,
                        gene_reaction_rule=reaction['gene_reaction_rule'])
                except Exception as e:
                    print(e, file)


class Command(BaseCommand):
    help = 'Link reaction and gene from json'

    def add_arguments(self, parser):
        parser.add_argument('gene_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['gene_path'])
