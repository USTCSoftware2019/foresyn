from abc import ABCMeta, abstractmethod
from cobra_wrapper.models import CobraModel, CobraMetabolite, CobraReaction
from bigg_database.models import Model as DataModel, Metabolite as DataMetabolite, Reaction as DataReaction
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
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


def data_metabolite_to_cobra_metabolite(key, value):
    try:
        data_metabolite_object = DataMetabolite.objects.get(key=value)
    except ObjectDoesNotExist:
        return None
    # relationships
    cobra_metabolite_object = CobraMetabolite()
    cobra_metabolite_object.formula = data_metabolite_object.formulae
    cobra_metabolite_object.name = data_metabolite_object.name
    cobra_metabolite_object.identifier = data_metabolite_object.bigg_id
    cobra_metabolite_object.charge = data_metabolite_object.charges
    cobra_metabolite_object.compartment = data_metabolite_object.bigg_id[-1]
    # cobra_metabolite_object.user
    return cobra_metabolite_object


def is_number(num):
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(num)
    if result:
        return True
    else:
        return False
