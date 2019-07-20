import json
from bigg_database.models import Reaction, Models
import os

for root, _, files in os.walk('D:\\Code\\iGEM\\reactions'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        bigg_id = content['bigg_id']
        name = content['name']

        database_links = content['database_links']
        pseudoreaction = content['pseudoreaction']
        reaction_string = content['reaction_string']

        reaction = Reaction.objects.create(bigg_id=bigg_id, name=name, reaction_string=reaction_string,
                                           pseudoreaction=pseudoreaction, database_links=database_links)
