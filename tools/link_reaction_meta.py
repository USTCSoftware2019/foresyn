import json
from bigg_database.models import Reaction,Metabolite,ReactionMetabolite
import os

for root, _, files in os.walk('D:\\Code\\iGEM\\reactions'):
    with open(os.path.join(root, files), 'r', encoding='utf-8') as f:
        content = json.loads(f.read())

        reaction_bigg_id = content['bigg_id']
        reaction_instance = Reaction.objects.get(bigg_id=reaction_bigg_id)
        for meta in content['metabolites']:
            meta_bigg_id = meta['bigg_id']
            meta_stoichiometry = meta['stoichiometry']
            meta_instance = Metabolite.objects.get(bigg_id=meta_bigg_id)
            ReactionMetabolite.objects.create(
                reaction=model_instance, metabolite=meta_instance,stoichiometry=meta_stoichiometry) 


