import json
from bigg_database.models import Metabolite
import os

for root, _, files in os.walk('D:\\Code\\iGEM\\metabolite'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        bigg_id = content['bigg_id']

        name = content['name']
        formulae = content['formulae']
        charges = content['charges']
        database_links = content['database_links']

        Metabolite.objects.create(
            bigg_id=bigg_id,name=name,formulae=formulae,
            charges=charges,database_links=database_links)


