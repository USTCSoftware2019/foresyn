from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.filter
def get_object_name(fav_obj):
    tp = fav_obj.target_content_type.model_class()
    pk = fav_obj.target_object_id
    obj = tp.objects.get(pk=pk)
    return obj.bigg_id

@register.filter
def get_object_source(fav_obj):
    return fav_obj.target_content_type

@register.simple_tag
def pack_favorite_button(fav_obj):
    ctp = fav_obj.target_content_type

    return render_to_string('utils/fav_button.html',
                            {'target_app': ctp.app_label,
                             'target_name': ctp.model,
                             'target_object_id': fav_obj.target_object_id,
                             'undo': True})