from django import template
from django.template.loader import render_to_string
from bigg_database.models import Model, Reaction, Gene, Metabolite
from share.models import ShareModel
from django.urls import reverse


register = template.Library()


@register.filter
def get_object_name(fav_obj):
    tp = fav_obj.target_content_type.model_class()
    pk = fav_obj.target_object_id
    obj = tp.objects.get(pk=pk)
    if tp != ShareModel:
        return obj.bigg_id
    else:
        return obj.name


@register.filter
def get_object_source(fav_obj):
    return fav_obj.target_content_type


@register.filter
def get_object_description(fav_obj):
    tp = fav_obj.target_content_type.model_class()
    if tp != Model:
        pk = fav_obj.target_object_id
        obj = tp.objects.get(pk=pk)
        return obj.name
    else:
        return ""


@register.simple_tag
def pack_favorite_button(fav_obj):
    ctp = fav_obj.target_content_type

    return render_to_string('utils/fav_button.html',
                            {'target_app': ctp.app_label,
                             'target_name': ctp.model,
                             'target_object_id': fav_obj.target_object_id,
                             'undo': True})


@register.simple_tag
def render_link_tag(obj):
    if obj is None:
        return '#'
    if hasattr(obj, 'object'):
        obj = obj.object
    model = obj.target_content_type.model_class()
    if model == Model:
        viewname = 'bigg_database:model_detail'
    elif model == Reaction:
        viewname = 'bigg_database:reaction_detail'
    elif model == Gene:
        viewname = 'bigg_database:gene_detail'
    elif model == Metabolite:
        viewname = 'bigg_database:metabolite_detail'
    elif model == ShareModel:
        viewname = 'share:shared_cobra_model'
    else:
        return '#'

    return reverse(viewname=viewname, args=(obj.target_object_id,))
