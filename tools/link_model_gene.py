import json
from bigg_database.models import Model, Gene
import os


for root, _, files in os.walk('D:\\Code\\iGEM\\models'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        model_bigg_id = content['id']
        model_instance = Model.objects.get(bigg_id=model_bigg_id)

        for gene in content['genes']:
            gene_bigg_id = gene['id']

            gene_instance = Gene.objects.get(bigg_id=gene_bigg_id)
            gene_instance.models.add(model_instance)
            gene_instance.save()
