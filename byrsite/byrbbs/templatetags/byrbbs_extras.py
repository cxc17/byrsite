# coding: utf-8

from django import template
import re


register = template.Library()


# 返回当前页之前的页数
@register.filter
def page_list_pre(page):
    page = int(page)
    if page <= 5:
        return range(1, page)
    else:
        return range(page-4, page)


# 返回当前页之后的页数
@register.filter
def page_list_next(page, page_max):
    page = int(page)
    if page_max - page < 5:
        return range(page+1, page_max+1)
    else:
        return range(page+1, page+5)


# 返回最多200字节的内容
@register.filter
def content_output_max(content):
    if len(content) < 200:
        return content
    else:
        return content[:200] + u" ..."


# 对输出的内容进行整理,如果含有关键字进行提取切分
@register.filter
def search_key(content, key):
    if len(content) < 200:
        content = content
    else:
        content = content[:200] + u" ..."

    content_iter = re.finditer("%s" % key, content, re.I)

    result = ""
    start = 0
    for citer in content_iter:
        end = citer.start()
        result += content[start:end]
        result = result + '<b>' + content[citer.start():citer.end()] + '</b>'
        start = citer.end()

    result += content[start:]
    return result


# 关键字判断
@register.filter
def judge_key(content, key):
    return re.match("%s" %key, content, re.I)


# 对搜索时间进行
@register.filter
def search_time(search_time):
    search_time = round(search_time, 3)

    return search_time


# 对图片的大小进行处理
@register.filter
def image_length(length):
    if length == 0:
        return 140
    elif length > 140:
        return 140
    else:
        return length


# 对搜索结果数目进行处理
@register.filter
def search_count(search_count):
    if search_count < 1000:
        return search_count
    elif search_count < 1000000:
        return str(search_count)[:-3] + ',' + str(search_count)[-3:]
    else:
        return str(search_count)[:-6] + ',' + str(search_count)[-6:-3] + ',' + str(search_count)[-3:]


# 对搜索结果数目进行处理
@register.filter
def menu_type(menu_type, now_type):
    if menu_type == now_type:
        return "menu_total_active"
    else:
        return "menu_total"
