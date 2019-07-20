import json
from bigg_database.models import Model
import os


for root, _, files in os.walk('D:\\Code\\iGEM\\models'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        bigg_id = content['id']

        compartments = [key for key in content['compartments'].iterkeys()]

        version = content['version']
        Model.objects.create(
            bigg_id=bigg_id, compartments=compartments, version=version)
