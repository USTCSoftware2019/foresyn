import json
import os

import django
from django.core.management.base import BaseCommand

from bigg_database.models import Model, ModelReaction, Reaction

from .progressbar import print_progressbar


def parse_all_files_in_dir(path):
    objects = {}
    print('Processing', path)

    for root, _, files in os.walk(path):
        total_len = len(files)
        for cnt, file in enumerate(files):
            print_progressbar(cnt + 1, total_len)
            with open(os.path.join(root, file), 'r') as json_file:
                try:
                    objects[file[:-5]] = json.load(json_file)
                except json.decoder.JSONDecodeError as e:
                    print(e, file)
    print('')
    return objects


def link(model, reaction, reaction_info):
    model = Model.objects.get(bigg_id=model)
    reaction = Reaction.objects.get(bigg_id=reaction)

    organism = reaction_info['organism']
    lower_bound = reaction_info['lower_bound']
    upper_bound = reaction_info['upper_bound']
    subsystem = reaction_info.get('subsystem')

    gene_reaction_rule = reaction_info['gene_reaction_rule']

    try:
        ModelReaction.objects.create(model=model,
                                     reaction=reaction,
                                     organism=organism,
                                     lower_bound=lower_bound,
                                     upper_bound=upper_bound,
                                     subsystem=subsystem,
                                     gene_reaction_rule=gene_reaction_rule)
    except Exception as e:
        print(e, model.id, reaction.id)


def organism_lookup(reaction, model, reactions):
    child_models = reactions[reaction]['models_containing_reaction']
    try:
        result_model = next(m for m in child_models if m['bigg_id'] == model)
    except StopIteration:
        print(reaction, model)
        exit()

    return result_model['organism']


def main(models_dirname, reactions_dirname):
    model_jsons = parse_all_files_in_dir(models_dirname)
    reaction_jsons = parse_all_files_in_dir(reactions_dirname)
    total_len = len(model_jsons)
    cnt = 0
    print('Linking')
    for model_id, model in model_jsons.items():
        cnt += 1
        print_progressbar(cnt, total_len)

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
                    # exit()
                    continue

            reaction['organism'] = organism_lookup(
                reaction['id'], model_id, reaction_jsons)
            link(model_id, reaction['id'], reaction)


class Command(BaseCommand):
    help = 'Link model and reaction from json'

    def add_arguments(self, parser):
        parser.add_argument('model_path', type=str)
        parser.add_argument('reaction_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['model_path'], kwargs['reaction_path'])
