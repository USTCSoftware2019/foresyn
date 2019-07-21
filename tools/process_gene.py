
import json
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Gene


def get_from_content(content, *argv):
    return {
        key: getattr(content, key)
        for key in argv
    }


root = sys.argv[1]
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
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
