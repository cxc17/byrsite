from django import template
import re


register = template.Library()


@register.filter
def page_list_pre(page):
    page = int(page)
    if page <= 5:
        return range(1, page)
    else:
        return range(page-4, page)


@register.filter
def page_list_next(page, page_max):
    page = int(page)
    if page_max - page <= 5:
        return range(page+1, page_max+1)
    else:
        return range(page+1, page+5)


@register.filter
def content_output_max(content):
    if len(content) < 200:
        return content
    else:
        return content[:200] + u" ..."


@register.filter
def search_key(content, key):
    if len(content) < 200:
        content = content
    else:
        content = content[:200] + u" ..."

    result = []
    if key in content:
        content_iter = re.finditer("%s" % key, content)

        start = 0
        for citer in content_iter:
            end = citer.start()
            result.append(content[start:end])
            result.append(key)
            start = citer.end()

        result.append(content[start:])
        return result
    else:
        result.append(content)
        return result


@register.filter
def search_time(search_time):
    search_time = round(search_time, 3)

    return search_time
