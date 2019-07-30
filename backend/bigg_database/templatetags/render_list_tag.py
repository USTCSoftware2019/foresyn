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


@register.inclusion_tag('bigg_database/list.html')
def render_list_tag(lst, model, view_name, **kwargs):
    """
    This is used to render all kinds of list, including gene_list, metabolite_list, model_list, reaction_list.
    This template tag just render url for them, as the url is hard to evaluate in template.

    Usage: {% render_list_tag result_list 'gene' 'model_gene_relationship_detail' id=model.id reverse=False %}

    :param lst: list of instances
    :param model: one of ('gene', 'model', 'reaction', 'metabolite')
    :param view_name: one of DetailViews in urls.py
    :param kwargs: 'id': if view_name is one of RelationShipDetailView, you may need to pass in an extra id.
                   'reverse': boolean. If True, it means this is a reverse lookup, extra id will be the second arg.
                              E.g., if you want to render list of reactions from model, reverse=False,
                              if you want to render list of models from reaction, reverse=True, default is False
    """
    for ins in lst:
        app_view_name = 'bigg_database:' + view_name
        if view_name in relp_views:
            try:
                if kwargs['reverse']:
                    ins.detail_url = reverse(app_view_name, args=(ins.id, kwargs['id']))
                else:
                    ins.detail_url = reverse(app_view_name, args=(kwargs['id'], ins.id))
                # Don't pass reverse and id to the template in case of some conflicts
            except KeyError:
                # no reverse. default is false
                ins.detail_url = reverse(app_view_name, args=(kwargs['id'], ins.id))
        else:
            ins.detail_url = reverse(app_view_name, args=(ins.id,))

    kwargs.pop('id', None)
    kwargs.pop('reverse', None)

    return {
        'list': lst,
        'model': model,
        **kwargs
    }
