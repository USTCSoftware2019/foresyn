from django.template import Library
from django.urls import reverse

register = Library()

search_url_construction = '{base_url}{prefix}?page={page}'


@register.inclusion_tag('bigg_database/page_index_display.html')
def calc_index_display_tag(paginator, search_url_prefix, **kwargs):
    page_item_list = []
    if paginator.num_pages >= 13:
        if paginator.number <= 5:
            for index in range(1, paginator.number + 4):
                page_item_list.append({
                    'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                          prefix=search_url_prefix,
                                                          page=index),
                    'active': False if index != paginator.number else True,
                    'display_stuff': index,
                    'disable': False
                })
            page_item_list.append({
                'url': '#',
                'active': False,
                'display_stuff': '...',
                'disable': True
            })
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=paginator.num_pages - 1),
                'active': False,
                'display_stuff': paginator.num_pages - 1,
                'disable': False
            })
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=paginator.num_pages),
                'active': False,
                'display_stuff': paginator.num_pages,
                'disable': False
            })
        elif paginator.number >= paginator.num_pages - 5:
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=1),
                'active': False,
                'display_stuff': 1,
                'disable': False
            })
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=2),
                'active': False,
                'display_stuff': 2,
                'disable': False
            })
            page_item_list.append({
                'url': '#',
                'active': False,
                'display_stuff': '...',
                'disable': True
            })
            for index in range(paginator.number - 3, paginator.num_pages + 1):
                page_item_list.append({
                    'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                          prefix=search_url_prefix,
                                                          page=index),
                    'active': False if index != paginator.number else True,
                    'display_stuff': index,
                    'disable': False
                })
        else:
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=1),
                'active': False,
                'display_stuff': 1,
                'disable': False
            })
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=2),
                'active': False,
                'display_stuff': 2,
                'disable': False
            })
            page_item_list.append({
                'url': '#',
                'active': False,
                'display_stuff': '...',
                'disable': True
            })
            for index in range(paginator.number - 3, paginator.number + 4):
                page_item_list.append({
                    'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                          prefix=search_url_prefix,
                                                          page=index),
                    'active': False if index != paginator.number else True,
                    'display_stuff': index,
                    'disable': False
                })
            page_item_list.append({
                'url': '#',
                'active': False,
                'display_stuff': '...',
                'disable': True
            })
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=paginator.num_pages - 1),
                'active': False,
                'display_stuff': paginator.num_pages - 1,
                'disable': False
            })

            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=paginator.num_pages),
                'active': False,
                'display_stuff': paginator.num_pages,
                'disable': False
            })
    else:
        for index in range(1, paginator.num_pages + 1):
            page_item_list.append({
                'url': search_url_construction.format(base_url=reverse('bigg_database:search'),
                                                      prefix=search_url_prefix,
                                                      page=index),
                'active': False if index != paginator.num_pages else True,
                'display_stuff': index,
                'disable': False
            })

    return {
        'page_items': page_item_list,
        **kwargs
    }
