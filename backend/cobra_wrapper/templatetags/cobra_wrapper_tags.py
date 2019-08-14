from django import template

register = template.Library()


@register.filter
def get_dict_value_with_key(dic, key):
    return dic[key]
