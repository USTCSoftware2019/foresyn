from django.template import Library
from django.urls import reverse

register = Library()

relp_views = [
    'model_metabolite_relationship_detail',
    'model_reaction_relationship_detail',
    'reaction_metabolite_relationship_detail',
    'reaction_gene_relationship_detail',
    'model_gene_relationship_detail',
]


@register.inclusion_tag('list.html')
def render_list_tag(lst, model, view_name, *args):
    """
    This is used to render all kinds of list, including gene_list, metabolite_list, model_list, reaction_list.
    This template tag just render url for them, as the url is hard to evaluate in template.

    Usage: {% render_list_tag result_list 'gene' 'model_gene_relationship_detail' model.id %}

    :param lst: list of instances
    :param model: one of ('gene', 'model', 'reaction', 'metabolite')
    :param view_name: one of DetailViews in urls.py
    :param args: if view_name is one of RelationShipDetailView, you may need to pass in an extra id.
    this id will be used to reverse url
    """
    for ins in list:
        if view_name in relp_views:
            ins.detail_url = reverse('bigg_database:' + view_name, args[0], ins.id)
        else:
            ins.detail_url = reverse('bigg_database:' + view_name, ins.id)

    return {
        'list': lst,
        'model': model,
    }
