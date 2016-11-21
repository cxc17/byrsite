# coding: utf-8

from django.db.models import Q
from django import template
import jieba
import re

from byrbbs.models import byr_stop_word

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
def content_output_max(content, key):
    keys_info = list(jieba.cut(key))
    if len(content) < 200:
        for key_info in keys_info:
            if key_info == " " or key_info == u" ":
                continue
            if re.findall(r"^\w$", key_info):
                content = re.sub(r"(\W)(%s)(\W)" % key_info, "\g<1><b>\g<2></b>\g<3>", content, flags=re.I)
            else:
                content = re.sub(re.escape("%s" % key_info), "<b>%s</b>" % key_info, content, flags=re.I)
        return content
    # 停用词
    stop_word = byr_stop_word.objects.filter(Q(id=2742))[0].word

    key_info_normal = []
    key_info_stop = []
    for i in keys_info:
        if i in stop_word:
            key_info_stop.append(i)
        else:
            key_info_normal.append(i)

    num = -1
    for key_info in key_info_normal:
        if key_info == " " or key_info == u" ":
            continue
        if re.findall(r"^\w+$", key_info):
            try:
                num = max(0, re.search(r"\W%s\W" % key_info, content, re.I).span()[0]-10)
            except:
                num = 0
        else:
            num = content.find(key_info)
        if num != -1:
            break
    if num == -1:
        for key_info in key_info_stop:
            if key_info == " " or key_info == u" ":
                continue
            if re.findall(r"^\w+$", key_info):
                try:
                    num = max(0, re.search(r"\W%s\W" % key_info, content, re.I).span()[0]-10)
                except:
                    num = 0
            else:
                num = content.find(key_info)
            if num != -1:
                break

    content = content[num:num+200] + u" ..."
    for key_info in keys_info:
        if key_info == " " or key_info == u" ":
            continue
        if re.findall(r"^\w+$", key_info):
            content = re.sub(r"(\W)(%s)(\W)" % key_info, "\g<1><b>\g<2></b>\g<3>", content, flags=re.I)
        else:
            content = re.sub(re.escape("%s" % key_info), "<b>%s</b>" % key_info, content, flags=re.I)
    return content


# 对输出的内容进行整理,如果含有关键字进行提取切分
@register.filter
def search_key(content, key):
    content_iter = re.finditer(re.escape("%s" % key), content, re.I)
    result = ""
    start = 0
    for citer in content_iter:
        end = citer.start()
        result += content[start:end]
        result = result + '<b>' + content[citer.start():citer.end()] + '</b>'
        start = citer.end()
    result += content[start:]
    return result


# 用户大写
@register.filter
def user_key(content, key):
    if content.lower() == key.lower():
        return '<b>' + content + '</b>'
    return content


# 用户登录地点
@register.filter
def last_site(result):
    if result.last_login_bupt != '':
        return u"北邮" + result.last_login_bupt
    else:
        return result.country_cn + result.province


# 关键字判断
@register.filter
def judge_key(content, key):
    return re.match("%s" % key, content, re.I)


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


# 对搜索日期进行处理
@register.filter
def date_type(date):
    if date == u'1':
        return "一天内"
    elif date == u'7':
        return "一周内"
    elif date == u'30':
        return "一月内"
    elif date == u'365':
        return "一年内"
    else:
        return u'时间不限'


# 对搜索类型进行处理
@register.filter
def search_type(search_type):
    if search_type == u'exact':
        return u"精确匹配"
    else:
        return u'所有结果'
