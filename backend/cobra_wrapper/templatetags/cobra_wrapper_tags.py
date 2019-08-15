from django import template

register = template.Library()


@register.filter
def get_dict_value_with_key(dic, key):
    return dic[key]


@register.filter
def check_result_status(fva_obj):
    if fva_obj.result:
        return 'OK'
    else:
        return 'Processing'
