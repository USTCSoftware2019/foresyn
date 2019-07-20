import json
from bigg_database.models import ModelMetabolite, Model, Metabolite
import os

for root, _, files in os.walk('D:\\Code\\iGEM\\models'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        model_bigg_id = content['id']
        model_instance = Model.objects.get(bigg_id=model_bigg_id)
        for meta in content['metabolites']:
            meta_bigg_id = meta['id']
            meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
            ModelMetabolite.objects.create(
                model=model_instance, metabolite=meta_instance)  # 还有organism没有加入

for root, _, files in os.walk('D:\\Code\\iGEM\\metabolite'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        meta_bigg_id_without_compartments = content['bigg_id']

        for compartments in content['metabolites']:
            meta_bigg_id = meta_bigg_id_without_compartments + \
                compartments['bigg_id']
            meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
            model_instance = Model.objects.get(
                bigg_id=content['model_bigg_id'])

            organism = compartments['organism']

            mm = ModelMetabolite.objects.get(
                metabolite=meta_instance, model=model_instance)

            mm.organism = organism
            mm.save()
