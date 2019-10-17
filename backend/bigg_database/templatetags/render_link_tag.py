from django.template import Library
from django.urls import reverse
from bigg_database.models import Model, Reaction, Gene, Metabolite

register = Library()


@register.simple_tag()
def render_link_tag(obj):
    if obj is None:
        return '#'
    if hasattr(obj, 'object'):
        obj = obj.object
    if isinstance(obj, Model):
        viewname = 'bigg_database:model_detail'
    elif isinstance(obj, Reaction):
        viewname = 'bigg_database:reaction_detail'
    elif isinstance(obj, Gene):
        viewname = 'bigg_database:gene_detail'
    elif isinstance(obj, Metabolite):
        viewname = 'bigg_database:metabolite_detail'
    else:
        return '#'

    return reverse(viewname=viewname, args=(obj.id,))
