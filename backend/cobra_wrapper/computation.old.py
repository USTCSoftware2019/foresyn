import cobra
from operator import attrgetter

import pandas as pd
from numpy import zeros

from cobra.core import get_solution
from cobra.flux_analysis.variability import flux_variability_analysis
from cobra.util.solver import linear_reaction_coefficients
from cobra.util.util import format_long_string


def metabolite_summary(model, met_str, solution=None, threshold=0.01, fva=None, names=False):
    """
    Quote from official documents.
    Return the values instead of print them.
    """
    met = model.metabolites.get_by_id(met_str)
    if names:
        emit = attrgetter('name')
    else:
        emit = attrgetter('id')
    if solution is None:
        met.model.slim_optimize(error_value=None)
        solution = get_solution(met.model, reactions=met.reactions)

    rxns = sorted(met.reactions, key=attrgetter("id"))
    rxn_id = list()
    rxn_name = list()
    flux = list()
    reaction = list()
    for rxn in rxns:
        rxn_id.append(rxn.id)
        rxn_name.append(emit(rxn))  # remove format_long_string
        flux.append(solution[rxn.id] * rxn.metabolites[met])
        txt = rxn.build_reaction_string(use_metabolite_names=names)
        reaction.append(txt)  # remove format_long_string

    flux_summary = pd.DataFrame({
        "id": rxn_name,
        "flux": flux,
        "reaction": reaction
    }, index=rxn_id)

    if fva is not None:
        if hasattr(fva, 'columns'):
            fva_results = fva
        else:
            fva_results = flux_variability_analysis(
                met.model, list(met.reactions), fraction_of_optimum=fva)

        flux_summary["maximum"] = zeros(len(rxn_id), dtype=float)
        flux_summary["minimum"] = zeros(len(rxn_id), dtype=float)
        for rxn in rxns:
            fmax = rxn.metabolites[met] * fva_results.at[rxn.id, "maximum"]
            fmin = rxn.metabolites[met] * fva_results.at[rxn.id, "minimum"]
            if abs(fmin) <= abs(fmax):
                flux_summary.at[rxn.id, "fmax"] = fmax
                flux_summary.at[rxn.id, "fmin"] = fmin
            else:
                # Reverse fluxes.
                flux_summary.at[rxn.id, "fmax"] = fmin
                flux_summary.at[rxn.id, "fmin"] = fmax

    assert flux_summary["flux"].sum() < 1E-6, "Error in flux balance"

    flux_summary = _process_flux_dataframe(flux_summary, fva, threshold)

    flux_summary['percent'] = 0
    total_flux = flux_summary.loc[flux_summary.is_input, "flux"].sum()

    flux_summary.loc[flux_summary.is_input, 'percent'] = \
        flux_summary.loc[flux_summary.is_input, 'flux'] / total_flux
    flux_summary.loc[~flux_summary.is_input, 'percent'] = \
        flux_summary.loc[~flux_summary.is_input, 'flux'] / total_flux

    flux_summary['percent'] = flux_summary.percent.apply(
        lambda x: '{:.0%}'.format(x))

    PRODUCING_REACTIONS_TABLE = []
    CONSUMING_REACTIONS_TABLE = []
    if fva is not None:
        for ids in flux_summary.index:
            if flux_summary.loc[ids, 'is_input']:
                PRODUCING_REACTIONS_TABLE.append((flux_summary.loc[ids, 'percent'],
                                                  flux_summary.loc[ids, 'flux'],
                                                  flux_summary.loc[ids, 'fva_fmt'],
                                                  flux_summary.loc[ids, 'id'],
                                                  flux_summary.loc[ids, 'reaction']))
            else:
                CONSUMING_REACTIONS_TABLE.append((flux_summary.loc[ids, 'percent'],
                                                  flux_summary.loc[ids, 'flux'],
                                                  flux_summary.loc[ids, 'fva_fmt'],
                                                  flux_summary.loc[ids, 'id'],
                                                  flux_summary.loc[ids, 'reaction']))
        # Return as a list of tuple, tuple(PERCENTAGE, FLUX, RANGE, RXN_ID, REACTION)
    else:
        for ids in flux_summary.index:
            if flux_summary.loc[ids, 'is_input']:
                PRODUCING_REACTIONS_TABLE.append((flux_summary.loc[ids, 'percent'],
                                                  flux_summary.loc[ids, 'flux'],
                                                  flux_summary.loc[ids, 'id'],
                                                  flux_summary.loc[ids, 'reaction']))
            else:
                CONSUMING_REACTIONS_TABLE.append((flux_summary.loc[ids, 'percent'],
                                                  flux_summary.loc[ids, 'flux'],
                                                  flux_summary.loc[ids, 'id'],
                                                  flux_summary.loc[ids, 'reaction']))
        # Return as a list of tuple, tuple(PERCENTAGE, FLUX, RXN_ID, REACTION)

    met_tag = "{0} ({1})".format(met.name, met.id)
    name_and_rxn = [met_tag, PRODUCING_REACTIONS_TABLE, CONSUMING_REACTIONS_TABLE]
    return name_and_rxn


def model_summary(model, solution=None, threshold=0.01, fva=None, names=False):
    """
    Quote from official documents.
    Return the values instead of print them.
    """
    if names:
        emit = attrgetter('name')
    else:
        emit = attrgetter('id')
    objective_reactions = linear_reaction_coefficients(model)
    boundary_reactions = model.exchanges
    summary_rxns = set(objective_reactions.keys()).union(boundary_reactions)

    if solution is None:
        model.slim_optimize(error_value=None)
        solution = get_solution(model, reactions=summary_rxns)

    # Create a dataframe of objective fluxes
    obj_fluxes = pd.DataFrame({key: solution[key.id] * value for key,
                               value in objective_reactions.items()},  # change iteritems to .items()
                              index=['flux']).T
    obj_fluxes['id'] = obj_fluxes.apply(
        lambda x: x.name.id, 1)  # remove format_long_string

    # Build a dictionary of metabolite production from the boundary reactions
    metabolites = {m for r in boundary_reactions for m in r.metabolites}
    index = sorted(metabolites, key=attrgetter('id'))
    metabolite_fluxes = pd.DataFrame({
        'id': [emit(m) for m in index],  # remove format_long_string
        'flux': zeros(len(index), dtype=float)
    }, index=[m.id for m in index])
    for rxn in boundary_reactions:
        for met, stoich in rxn.metabolites.items():
            metabolite_fluxes.at[met.id, 'flux'] += stoich * solution[rxn.id]

    # Calculate FVA results if requested
    if fva is not None:
        # if len(index) != len(boundary_reactions):
        #     LOGGER.warning(
        #         "There exists more than one boundary reaction per metabolite. "
        #         "Please be careful when evaluating flux ranges.")
        metabolite_fluxes['fmin'] = zeros(len(index), dtype=float)
        metabolite_fluxes['fmax'] = zeros(len(index), dtype=float)
        if hasattr(fva, 'columns'):
            fva_results = fva
        else:
            fva_results = flux_variability_analysis(
                model, reaction_list=boundary_reactions,
                fraction_of_optimum=fva)

        for rxn in boundary_reactions:
            for met, stoich in rxn.metabolites.items():
                fmin = stoich * fva_results.at[rxn.id, 'minimum']
                fmax = stoich * fva_results.at[rxn.id, 'maximum']
                # Correct 'max' and 'min' for negative values
                if abs(fmin) <= abs(fmax):
                    metabolite_fluxes.at[met.id, 'fmin'] += fmin
                    metabolite_fluxes.at[met.id, 'fmax'] += fmax
                else:
                    metabolite_fluxes.at[met.id, 'fmin'] += fmax
                    metabolite_fluxes.at[met.id, 'fmax'] += fmin

    # Generate a dataframe of boundary fluxes
    metabolite_fluxes = _process_flux_dataframe(
        metabolite_fluxes, fva, threshold)

    IN_FLUXES_TABLE = []
    OUT_FLUXES_TABLE = []
    OBJ_TABLE = []
    if fva is not None:
        for ids in metabolite_fluxes.index:
            if metabolite_fluxes.loc[ids, 'is_input']:
                IN_FLUXES_TABLE.append((metabolite_fluxes.loc[ids, 'id'],
                                        metabolite_fluxes.loc[ids, 'flux'],
                                        metabolite_fluxes.loc[ids, 'fva_fmt']))
            else:
                OUT_FLUXES_TABLE.append((metabolite_fluxes.loc[ids, 'id'],
                                         metabolite_fluxes.loc[ids, 'flux'],
                                         metabolite_fluxes.loc[ids, 'fva_fmt']))
        # Return as a list of tuple, tuple(ID, FLUX, RANGE)
    else:
        for ids in metabolite_fluxes.index:
            if metabolite_fluxes.loc[ids, 'is_input']:
                IN_FLUXES_TABLE.append((metabolite_fluxes.loc[ids, 'id'],
                                        metabolite_fluxes.loc[ids, 'flux']))
            else:
                OUT_FLUXES_TABLE.append((metabolite_fluxes.loc[ids, 'id'],
                                         metabolite_fluxes.loc[ids, 'flux']))
        # Return as a list of tuple, tuple(ID, FLUX)
    for ids in obj_fluxes.index:
        OBJ_TABLE.append((obj_fluxes.loc[ids, 'id'],
                          obj_fluxes.loc[ids, 'flux']))

    return [IN_FLUXES_TABLE, OUT_FLUXES_TABLE, OBJ_TABLE]


def _process_flux_dataframe(flux_dataframe, fva, threshold):
    """Some common methods for processing a database of flux information into
    print-ready formats. Used in both model_summary and metabolite_summary. """

    abs_flux = flux_dataframe['flux'].abs()
    flux_threshold = threshold * abs_flux.max()

    # Drop unused boundary fluxes
    if fva is None:
        flux_dataframe = flux_dataframe.loc[
            abs_flux >= flux_threshold, :].copy()
    else:
        flux_dataframe = flux_dataframe.loc[
            (abs_flux >= flux_threshold) | (flux_dataframe['fmin'].abs() >= flux_threshold) | (
                flux_dataframe['fmax'].abs() >= flux_threshold), :
        ].copy()
        # Why set to zero? If included show true value?
        # flux_dataframe.loc[
        #     flux_dataframe['flux'].abs() < flux_threshold, 'flux'] = 0

    # Make all fluxes positive
    if fva is None:
        flux_dataframe['is_input'] = (flux_dataframe['flux'] >= 0)
        flux_dataframe['flux'] = flux_dataframe['flux'].abs()
    else:

        def get_direction(x):
            """ decide whether or not to reverse a flux to make it positive """

            if x.flux < 0:
                return -1
            elif x.flux > 0:
                return 1
            elif (x.fmax > 0) & (x.fmin <= 0):
                return 1
            elif (x.fmax < 0) & (x.fmin >= 0):
                return -1
            elif ((x.fmax + x.fmin) / 2) < 0:
                return -1
            else:
                return 1

        # Anoning lint error. Consider to disable IDE lint for this part
        sign = flux_dataframe.apply(get_direction, 1)

        flux_dataframe['is_input'] = sign == 1

        flux_dataframe.loc[:, ['flux', 'fmin', 'fmax']] = \
            flux_dataframe.loc[:, ['flux', 'fmin', 'fmax']].multiply(
                sign, 0).astype('float').round(6)

        def _(x):
            return x if abs(x) > 1E-6 else 0

        flux_dataframe.loc[:, ['flux', 'fmin', 'fmax']] = \
            flux_dataframe.loc[:, ['flux', 'fmin', 'fmax']].applymap(_)

    if fva is not None:
        flux_dataframe['fva_fmt'] = flux_dataframe.apply(
            lambda x: ("[{0.fmin:" + "}, {0.fmax:" + "}]").format(x), 1)

        flux_dataframe = flux_dataframe.sort_values(
            by=['flux', 'fmax', 'fmin', 'id'],
            ascending=[False, False, False, True])

    else:
        flux_dataframe = flux_dataframe.sort_values(
            by=['flux', 'id'], ascending=[False, True])

    return flux_dataframe


def growth_media_change(model, media, change):
    if media in model.medium.keys():
        with model:
            medium = model.medium
            medium[media] = change
            model.medium = medium
            return model.slim_optimize()
    else:
        raise "Your metabolite must be in the boundary reactions"


# a = metabolite_summary(model, 'atp_c')
# print(a)
# b = model_summary(model)
# print(b)
# print(growth_media_change(model, 'EX_nh4_e', 10))
# flux_variability_analysis(model, model.reactions[:10], fraction_of_optimum = 0.9)
