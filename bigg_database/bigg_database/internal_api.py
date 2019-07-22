from bigg_database.models import Gene, Metabolite, Model, Reaction


def get_model_by_id(bigg_id):
    return Model.objects.get(bigg_id=bigg_id)


def get_reaction_by_id(bigg_id):
    return Reaction.objects.get(bigg_id=bigg_id)


def get_metabolite_by_id(bigg_id):
    return Metabolite.objects.get(bigg_id=bigg_id)


def get_gene_by_id(bigg_id):
    return Gene.objects.get(bigg_id=bigg_id)
