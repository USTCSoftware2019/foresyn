from cobra_wrapper.models import CobraMetabolite, CobraReaction
from bigg_database.models import Metabolite as DataMetabolite, Reaction as DataReaction
from django.core.exceptions import ObjectDoesNotExist


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
                f = float(index)
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


def data_metabolite_to_cobra_metabolite(key, value, user):
    try:
        # print("data_metabolite_to_cobra_metabolite()", key, value)
        data_metabolite_object = DataMetabolite.objects.get(**{key: value})
    except ObjectDoesNotExist:
        return None
    # relationships
    cobra_metabolite_object = CobraMetabolite()
    cobra_metabolite_object.cobra_id = data_metabolite_object.bigg_id
    cobra_metabolite_object.formula = data_metabolite_object.formulae
    cobra_metabolite_object.name = data_metabolite_object.name
    if data_metabolite_object.charges:
        cobra_metabolite_object.charge = data_metabolite_object.charges
    cobra_metabolite_object.compartment = data_metabolite_object.bigg_id[-1]
    cobra_metabolite_object.owner = user
    return cobra_metabolite_object


def data_reaction_to_cobra_reaction(user, key=None, value=None, data_reaction_object=None, **params):
    if data_reaction_object is None:
        try:
            data_reaction_object = DataReaction.objects.get(**{key: value})
        except ObjectDoesNotExist:
            return None

    cobra_reaction_object = CobraReaction()

    # Add metabolites
    reaction_string = data_reaction_object.reaction_string
    (metabolite_names, coefficients) = reaction_string_to_metabolites(reaction_string)

    cobra_reaction_object.coefficients = coefficients

    # relationship
    cobra_reaction_object.name = data_reaction_object.name
    cobra_reaction_object.identifier = data_reaction_object.bigg_id
    gene_reaction_rules = [gene.gene_reaction_rule for gene in data_reaction_object.reactiongene_set.all()]
    cobra_reaction_object.gene_reaction_rule = " or ".join(gene_reaction_rules)

    if params:
        cobra_reaction_object.subsystem = params["subsystem"]
        cobra_reaction_object.upper_bound = params["upper_bound"]
        cobra_reaction_object.lower_bound = params["lower_bound"]
        # cobra_reaction_object.objective_coefficient = params["objective_coefficient"]

    cobra_reaction_object.owner = user
    cobra_reaction_object.cobra_id = data_reaction_object.bigg_id
    cobra_reaction_object.save()

    for name in metabolite_names:
        cobra_metabolite_object = data_metabolite_to_cobra_metabolite(key="bigg_id", value=name, user=user)
        if cobra_metabolite_object is None:
            return None
        try:
            cobra_metabolite_object = CobraMetabolite.objects.get(owner_id=user,
                                                                  cobra_id=cobra_metabolite_object.cobra_id)
        except ObjectDoesNotExist:
            cobra_metabolite_object.save()
        cobra_reaction_object.metabolites.add(cobra_metabolite_object)
    return cobra_reaction_object
