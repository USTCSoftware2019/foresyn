from django.template import Library
from django.urls import reverse

register = Library()

view_map = {
    'model': 'bigg_database:model_detail',
    'reaction': 'bigg_database:reaction_detail',
    'gene': 'bigg_database:gene_detail',
    'metabolite': 'bigg_database:metabolite_detail'
}


@register.simple_tag()
def render_link_tag(obj, search_model):
    if obj is None:
        return '#'
    viewname = view_map.get(search_model)
    if not viewname:
        return '#'

    return reverse(viewname=viewname, args=(obj.django_orm_id,))
