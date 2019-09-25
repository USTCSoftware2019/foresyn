from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    url = context['request'].GET.copy()
    for k, v in kwargs.items():
        url[k] = v
    for k in [k for k, v in url.items() if not v]:
        del url[k]
    return url.urlencode()
