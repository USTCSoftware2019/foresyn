from django import template

register = template.Library()


@register.filter
def access_dict(dic, key):
    return dic[key]


@register.filter
def check_result_status(fva_obj):
    if fva_obj.result:
        return 'OK'
    elif fva_obj.task_id:
        return 'Processing'
    else:
        return 'Failed'


@register.filter
def split_with_comma(str_value):
    return str_value.split(',')
