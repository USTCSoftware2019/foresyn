from bigg_database.models import Metabolite as DataMetabolite
from django.core.exceptions import ObjectDoesNotExist
import cobra


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
    metabolites_objects = []
    for m in metabolites:
        try:
            data_metabolite_object = DataMetabolite.objects.get(bigg_id=m)
        except ObjectDoesNotExist:
            return None
        bigg_id = data_metabolite_object.bigg_id
        formula = data_metabolite_object.formulae[0]
        name = data_metabolite_object.name
        compartment = data_metabolite_object.bigg_id[-1]
        new_metabolite = cobra.Metabolite(bigg_id, formula=formula,
                                          name=name,
                                          compartment=compartment)
        metabolites_objects.append(new_metabolite)

    return dict(zip(metabolites_objects, coefficients))
