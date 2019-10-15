# FIXME(myl7): Remove metabolites and reactions
# from cobra_wrapper.models import CobraMetabolite, CobraReaction
from bigg_database.models import Metabolite as DataMetabolite, Reaction as DataReaction
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


def reaction_string_to_metabolites(reaction_string):
    metabolites = []
    coefficients = []
    right = False
    str_list = iter(reaction_string.split(' '))
    for index in str_list:
        if index != "+" and index != '':
            if index == "&#8652;":
                right = True
                continue
            try:
                # f = float(index)
                if right:
                    coefficients.append(float(index))
                else:
                    coefficients.append(float("-" + index))
                # if next(str_list) == '':
                #     continue
                metabolites.append(next(str_list))
            except Exception:
                if right:
                    coefficients.append(1.0)
                else:
                    coefficients.append(-1.0)
                metabolites.append(index)
    return metabolites, coefficients
