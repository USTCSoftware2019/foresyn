
import json
from bigg_database.models import Gene
import os

for root, _, files in os.walk('D:\\Code\\iGEM\\models'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        genes = json.loads(f.read())['genes']

        for gene in genes:
            bigg_id = gene['id']
            name = gene['name']
            Gene.objects.create(bigg_id=bigg_id, name=name)
