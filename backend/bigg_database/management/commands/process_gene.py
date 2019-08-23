
import asyncio
import json
import os

from django.core.management.base import BaseCommand

from bigg_database.models import Gene

from .progressbar import print_progressbar


def get_from_content(content, *argv):
    return {
        key: content[key]
        for key in argv
    }


type_default = {
    'int': 0,
    'str': '',
    'json': r'{}',
    'bool': True,
}


def avoid_null(stuff, val_type, *argv):
    for key in argv:
        stuff[key] = stuff[key] or type_default[val_type]
    return stuff


def main(gene_path):
    files_list = [os.path.join(gene_path, file)
                  for file in os.listdir(gene_path)
                  if not os.path.isdir(os.path.join(gene_path, file))]
    total_len = len(files_list)

    for cnt, file in enumerate(files_list):
        print_progressbar(cnt + 1, total_len)
        with open(file, 'r', encoding='utf-8') as f:
            try:
                content = json.loads(f.read())
            except Exception as e:
                print(e, file)
                continue

            try:
                stuff = get_from_content(content,
                                         'rightpos', 'name', 'chromosome_ncbi_accession',
                                         'mapped_to_genbank', 'leftpos', 'database_links',
                                         'strand', 'protein_sequence', 'genome_name',
                                         'dna_sequence', 'bigg_id', 'genome_ref_string')
                stuff = avoid_null(stuff, 'int', 'rightpos', 'leftpos')
                stuff = avoid_null(stuff, 'bool', 'mapped_to_genbank')
                stuff = avoid_null(stuff, 'str', 'name', 'dna_sequence',
                                   'genome_ref_string', 'protein_sequence', 'genome_name',
                                   'chromosome_ncbi_accession', 'strand')
            except AttributeError as e:
                print(e, file)
                continue
            try:
                Gene.objects.create(**stuff)
            except Exception as e:
                print(e, file)


class Command(BaseCommand):
    help = 'Generate gene data from json'

    def add_arguments(self, parser):
        parser.add_argument('gene_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['gene_path'])
