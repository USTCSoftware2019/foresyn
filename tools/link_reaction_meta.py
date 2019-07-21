
import sys
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Metabolite, Model, ModelMetabolite

root = sys.argv[1]
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        reaction_bigg_id = content['bigg_id']
        reaction_instance = Reaction.objects.get(bigg_id=reaction_bigg_id)
        for meta in content['metabolites']:
            meta_bigg_id = meta['bigg_id'] + '_' + meta['compartment_bigg_id']
            meta_stoichiometry = meta['stoichiometry']
            meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
            ReactionMetabolite.objects.create(
                reaction=model_instance, metabolite=meta_instance, stoichiometry=meta_stoichiometry)
