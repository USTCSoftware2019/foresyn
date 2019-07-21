
import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Metabolite


def get_from_content(content, *argv):
    return {
        key: getattr(content, key)
        for key in argv
    }


def main(gene_path):
    for file in os.listdir(gene_path):
        if os.path.isdir(file):
            continue
        with open(os.path.join(gene_path, file), 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                print(e, file)
                continue

            try:
                stuff = get_from_content(content,
                                         'rightpos', 'name', 'chromosome_ncbi_accession',
                                         'mapped_to_genbank', 'leftpos', 'database_links',
                                         'strand', 'protein_sequence', 'genome_name',
                                         'dna_sequence', 'bigg_id', 'genome_ref_string')
            except KeyError as e:
                print(e, file)
                continue

            Gene.objects.create(**stuff)


class Command(BaseCommand):
    help = 'Generate gene data from json'

    def add_arguments(self, parser):
        parser.add_argument('gene_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['gene_path'])
