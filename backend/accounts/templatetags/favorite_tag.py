from django import template
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from accounts.models import Favorite

register = template.Library()


@register.simple_tag(takes_context=True)
def favorite_button(context, target):
    user = context['request'].user

    # do nothing when user isn't authenticated
    if not user.is_authenticated:
        return ''

    if not target._meta:
        target_app = target.app_label
        target_name = target.model_name
        target_content_type = ContentType.objects.get(app_label=target_app, model=target_name)
        target_object_id = target.pk
    else:
        target_app = target._meta.app_label
        target_name = target._meta.object_name
        target_content_type = ContentType.objects.get_for_model(target)
        target_object_id = target.id
    undo = False
    if user.favorite_set.filter(target_content_type=target_content_type,
                                target_object_id=target_object_id):
        undo = True

    return render_to_string('utils/fav_button.html',
                            {'target_app': target_app,
                             'target_name': target_name,
                             'target_object_id': target_object_id,
                             'undo': undo})
