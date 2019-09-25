from django.template import Library

register = Library()


@register.inclusion_tag('bigg_database/page_index_display.html', takes_context=True)
def calc_index_display_tag(context, adjacent_pages=2):
    start_page = context['page_obj'].number - adjacent_pages
    display_first = True
    display_last = True

    if start_page <= 2:
        start_page = 1
        display_first = False

    end_page = context['page_obj'].number + adjacent_pages

    if end_page >= context['paginator'].num_pages - 1:
        end_page = context['paginator'].num_pages
        display_last = False

    page_numbers = range(start_page, end_page + 1)
    return {
        'page_obj': context['page_obj'],
        'paginator': context['paginator'],
        'page_numbers': page_numbers,
        'display_first': display_first,
        'display_last': display_last,
        'request': context['request'],
    }
