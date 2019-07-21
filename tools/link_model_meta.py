
import sys
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Metabolite, Model, ModelMetabolite

print('models')
root = sys.argv[1]
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
        try:
            content = json.loads(f.read())
        except json.decoder.JSONDecodeError:
            print(file)
        model_bigg_id = content['id']
        model_instance = Model.objects.get(bigg_id=model_bigg_id)
        for meta in content['metabolites']:
            meta_bigg_id = meta['id']
            meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
            ModelMetabolite.objects.create(
                model=model_instance, metabolite=meta_instance)  # 还有organism没有加入

print('meta')

root = sys.argv[2]
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        meta_bigg_id_without_compartments = content['bigg_id']

        for compartment in content['compartments_in_models']:
            meta_bigg_id = meta_bigg_id_without_compartments + '_' + \
                compartment['bigg_id']
            meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
            model_instance = Model.objects.get(
                bigg_id=model_bigg_id)

            mm = ModelMetabolite.objects.get(
                metabolite=meta_instance, model=model_instance)

            mm.organism = compartment['organism']
            mm.save()
