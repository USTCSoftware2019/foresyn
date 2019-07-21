import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Reaction, Model

# root = 'D:\\Code\\iGEM\\bigg_data\\data\\reactions'
root = '/home/elsa/data/data/reactions'
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
            bigg_id = content['bigg_id']
            name = content['name'] or ''

            database_links = content['database_links']
            pseudoreaction = content['pseudoreaction']
            reaction_string = content['reaction_string']
        except KeyError as e:
            print(e, file)
            continue
        try:
            reaction = Reaction.objects.create(bigg_id=bigg_id, name=name, reaction_string=reaction_string,
                                               pseudoreaction=pseudoreaction, database_links=database_links)
        except django.db.utils.IntegrityError as e:
            print(e, file)
