import io
import re
from typing import List, Dict, Any

import cobra


def load_sbml(sbml_content: str) -> cobra.Model:
    sbml_file = io.StringIO(sbml_content)
    return cobra.io.read_sbml_model(sbml_file)


def dump_sbml(cobra_model: cobra.Model) -> str:
    sbml_file = io.StringIO()
    cobra.io.write_sbml_model(cobra_model, sbml_file)
    sbml_file.seek(0)
    return sbml_file.read()


def get_reaction_json(reaction: cobra.Reaction) -> Dict[str, Any]:
    return {
        'cobra_id': reaction.id,
        'name': reaction.name,
        'subsystem': reaction.subsystem,
        'lower_bound': reaction.lower_bound,
        'upper_bound': reaction.upper_bound,
        'gene_reaction_rule': reaction.gene_reaction_rule,
        'reaction_str': reaction.reaction,
        'metabolites': [metabolite.name for metabolite in reaction.metabolites],
        'genes': [gene.name for gene in reaction.genes],
    }


def restore_reaction_by_json(cobra_model: cobra.Model, info: Dict[str, Any]) -> cobra.Reaction:
    reaction = cobra.Reaction(id=info['cobra_id'], name=info['name'], subsystem=info['subsystem'],
                              lower_bound=info['lower_bound'], upper_bound=info['upper_bound'])
    cobra_model.add_reactions([reaction])
    reaction.gene_reaction_rule = info['gene_reaction_rule']
    return reaction


def ensure_model_metabolites(cobra_model: cobra.Model, checked_metabolites: List[str]):
    metabolite_id_list = [metabolite.id for metabolite in cobra_model.metabolites]
    for value in checked_metabolites:
        if value not in metabolite_id_list:
            return False
    return True


def clean_comma_separated_str(form, value: str) -> str:
    return ','.join([item.strip() for item in value.split(',') if re.fullmatch(r'[a-zA-Z0-9_-]+', item.strip())])


def load_comma_separated_str(value: str) -> List[str]:
    return value.split(',') if value else []


COENZYME_PREFIXES = ['nadn', 'nad', 'nadph', 'nadp', 'atp', 'fmn', 'fmnh2', 'fad', 'fadh2']


def is_coenzyme(name: str):
    for coenzyme_prefix in COENZYME_PREFIXES:
        if re.match(r'^{}(?:$|_)'.format(coenzyme_prefix), name):
            return True
    return False
