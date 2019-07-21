import sys
import json
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

# 防止在格式化代码时将这个放在django初始化之前
if True:
    from bigg_database.models import Model

root = sys.argv[1]
for file in os.listdir(root):
    if os.path.isdir(file):
        continue
    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        bigg_id = content['id']

        compartments = [key for key in content['compartments'].keys()]

        version = content['version']
        Model.objects.create(
            bigg_id=bigg_id, compartments=compartments, version=version)
