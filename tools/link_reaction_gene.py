
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Gene, Reaction, ReactionGene

root = 'D:\\Code\\iGEM\\bigg_data\\data\\gene'  # for windows
# root = '/mnt/d/Code/iGEM/models'
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
        try:
            content = json.loads(f.read())
        except json.decoder.JSONDecodeError as e:
            print(e, file)

        gene_bigg_id = content['bigg_id']
        gene_instance = Gene.objects.get(bigg_id=gene_bigg_id)
        
        for reaction in content['reactions']:
            reaction_bigg_id = reaction['bigg_id']
            reaction_instance = Reaction.objects.get(bigg_id=reaction_bigg_id)
            ReactionGene.objects.create(
                reaction=reaction_instance, gene=gene_instance,
                gene_reaction_rule=reaction['gene_reaction_rule'])
