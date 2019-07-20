
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Metabolite

root = 'D:\\Code\\iGEM\\bigg_data\\data\\metabolites'  # for windows
# root = '/mnt/d/Code/iGEM/models'
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
        try:
            content = json.loads(f.read())
        except json.decoder.JSONDecodeError:
            print(file)

        bigg_id = content['bigg_id']
        name = content['name']
        formulae = content['formulae']
        try:
            charges = content['charges'][0]
        except IndexError as e:
            charges = None
        database_links = content['database_links']

        Metabolite.objects.create(
            bigg_id=bigg_id, name=name, formulae=formulae,
            charges=charges, database_links=database_links)
