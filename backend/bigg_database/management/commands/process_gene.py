
import asyncio
import json
import os
import aiofiles
from django.core.management.base import BaseCommand
from .progressbar import print_progressbar
from bigg_database.models import Gene


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


def process_gene_content(content, file_path):
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
        print(e, file_path)
        return
    try:
        Gene.objects.create(**stuff)
    except Exception as e:
        print(e, file_path)


async def process_gene_async(file_path):
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
        try:
            content = json.loads(await f.read())
        except Exception as e:
            print(e, file_path)
            return
        process_gene_content(content, file_path)


def main(gene_path):
    files_list = [os.path.join(gene_path, file)
                  for file in os.listdir(gene_path)
                  if not os.path.isdir(os.path.join(gene_path, file))]
    interval = 30
    file_count = len(files_list)
    loop = asyncio.get_event_loop()

    print_progressbar(0, file_count, length=50)
    processed_file_cnt = 0

    for file in [files_list[i:min(i + interval, file_count)] for i in range(0, file_count, interval)]:
        tasks = [process_gene_async(f) for f in file]
        loop.run_until_complete(asyncio.wait(tasks))

        processed_file_cnt += 30
        print_progressbar(min(processed_file_cnt, file_count), file_count, length=50)
    loop.close()


class Command(BaseCommand):
    help = 'Generate gene data from json'

    def add_arguments(self, parser):
        parser.add_argument('gene_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['gene_path'])
