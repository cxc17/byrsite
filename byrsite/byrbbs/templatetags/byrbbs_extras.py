from django import template

register = template.Library()


@register.filter
def page_list_pre(page):
    if page <= 5:
        return range(1, page)
    else:
        return range(page-4, page)


@register.filter
def page_list_next(page, page_max):
    if page_max - page <= 5:
        return range(page+1, page_max+1)
    else:
        return range(page+1, page+5)
