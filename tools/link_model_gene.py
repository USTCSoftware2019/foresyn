
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Gene, Model

root = sys.argv[1]
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        model_bigg_id = content['id']
        model_instance = Model.objects.get(bigg_id=model_bigg_id)

        for gene in content['genes']:
            gene_bigg_id = gene['id']

            gene_instance = Gene.objects.get(bigg_id=gene_bigg_id)
            gene_instance.models.add(model_instance)
            gene_instance.save()
