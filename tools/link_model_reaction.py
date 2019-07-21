import json
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigg_database.settings')

django.setup()

if True:
    from bigg_database.models import Model, Reaction, ModelReaction


def parse_all_files_in_dir(path):
    objects = {}

    for root, dirs, files in os.walk(path):
        for file in files:
            with open(os.path.join(root, file), 'r') as json_file:
                objects[file[:-5]] = json.load(json_file)

    return objects


def link(model, reaction, reaction_info):
    model = Model.objects.get(bigg_id=model)
    reaction = Reaction.objects.get(bigg_id=reaction)

    organism = reaction_info['organism']
    lower_bound = reaction_info['lower_bound']
    upper_bound = reaction_info['upper_bound']
    subsystem = reaction_info.get('subsystem')

    gene_reaction_rule = reaction_info['gene_reaction_rule']

    ModelReaction.objects.create(model=model,
                                 reaction=reaction,
                                 organism=organism,
                                 lower_bound=lower_bound,
                                 upper_bound=upper_bound,
                                 subsystem=subsystem,
                                 gene_reaction_rule=gene_reaction_rule)


def organism_lookup(reaction, model, reactions):
    child_models = reactions[reaction]['models_containing_reaction']
    try:
        result_model = next(m for m in child_models if m['bigg_id'] == model)
    except StopIteration:
        print(reaction, model)
        exit()

    return result_model['organism']


def main():
    if len(sys.argv) < 3:
        print("Usage: model_reaction.py path_to_models path_to_reactions")
        return

    models_dirname = sys.argv[1]
    reactions_dirname = sys.argv[2]

    model_jsons = parse_all_files_in_dir(models_dirname)
    reaction_jsons = parse_all_files_in_dir(reactions_dirname)

    for model_id, model in model_jsons.items():
        reactions = model['reactions']

        for reaction in reactions:
            if reaction['id'] not in reaction_jsons:
                """
                try:
                    reaction['id'] = next(original_id 
                                          for original_id in reaction['notes']['original_bigg_ids']
                                          if original_id in reaction_jsons)
                except StopIteration:
                    id_rmcopy = reaction['id'][:-6]
                    if id_rmcopy in reaction_jsons:
                        reaction['id'] = id_rmcopy
                    else:
                        print('No such reaction named ' + reaction['id'])
                        exit()
                """
                id_rmcopy = reaction['id'][:-6]
                if id_rmcopy in reaction_jsons:
                    reaction['id'] = id_rmcopy
                else:
                    print('No such reaction named ' + reaction['id'])
                    exit()

            reaction['organism'] = organism_lookup(reaction['id'], model_id, reaction_jsons)
            link(model_id, reaction['id'], reaction)


if __name__ == '__main__':
    main()

