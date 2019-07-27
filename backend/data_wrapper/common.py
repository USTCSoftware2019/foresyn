from cobra_wrapper.models import CobraMetabolite, CobraReaction
from bigg_database.models import Metabolite as DataMetabolite, Reaction as DataReaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import re


def reaction_string_to_metabolites(reaction_string):
    metabolites = []
    coefficients = []
    right = False
    str_list = iter(reaction_string.split(' '))
    for index in str_list:
        if index != "+":
            if index == "&#8652;":
                right = True
                continue
            if is_number(index):
                if right:
                    coefficients.append(float(index))
                else:
                    coefficients.append(float("-" + index))
                metabolites.append(next(str_list))
            else:
                if right:
                    coefficients.append(1.0)
                else:
                    coefficients.append(-1.0)
                metabolites.append(index)
    return metabolites, coefficients


def data_metabolite_to_cobra_metabolite(key, value, user):
    try:
        data_metabolite_object = DataMetabolite.objects.get(**{key: value})
    except ObjectDoesNotExist:
        return None
    # relationships
    cobra_metabolite_object = CobraMetabolite()
    cobra_metabolite_object.formula = data_metabolite_object.formulae
    cobra_metabolite_object.name = data_metabolite_object.name
    cobra_metabolite_object.identifier = data_metabolite_object.bigg_id
    cobra_metabolite_object.charge = data_metabolite_object.charges
    cobra_metabolite_object.compartment = data_metabolite_object.bigg_id[-1]
    # cobra_metabolite_object.user = user
    return cobra_metabolite_object


def data_reaction_to_cobra_reaction(key, value, user, data_reaction_object=None, **params):
    if data_reaction_object is None:
        try:
            data_reaction_object = DataReaction.objects.get(**{key: value})
        except ObjectDoesNotExist:
            return JsonResponse("error")

    cobra_reaction_object = CobraReaction()

    # Add metabolites first
    reaction_string = data_reaction_object.reaction_string
    (metabolite_names, coefficients) = reaction_string_to_metabolites(reaction_string)
    for name in metabolite_names:
        cobra_metabolite_object = data_metabolite_to_cobra_metabolite("bigg_id", name)
        cobra_reaction_object.save()
        cobra_reaction_object.metabolites.add(cobra_metabolite_object)
    cobra_reaction_object.coefficients = coefficients
    # relationship
    cobra_reaction_object.name = data_reaction_object.name
    cobra_reaction_object.identifier = data_reaction_object.bigg_id
    gene_reaction_rules = [gene.gene_reaction_rule for gene in data_reaction_object.reactiongene_set.all()]
    cobra_reaction_object.gene_reaction_rule = " or ".join(gene_reaction_rules)

    if params is not {}:
        cobra_reaction_object.subsystem = params["subsystem"]
        cobra_reaction_object.upper_bound = params["upper_bound"]
        cobra_reaction_object.lower_bound = params["lower_bound"]
        # cobra_reaction_object.objective_coefficient = params["objective_coefficient"]

    # cobra_reaction_object.user = user
    return cobra_reaction_object


def is_number(num):
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(num)
    if result:
        return True
    else:
        return False
