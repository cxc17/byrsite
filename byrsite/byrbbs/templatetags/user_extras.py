# coding: utf-8

from django import template
import json

register = template.Library()


# 对图片的大小进行处理
@register.filter
def image_length(length):
    if length == 0:
        return 140
    elif length > 140:
        return 140
    else:
        return length


# 用户登录地点
@register.filter
def last_site(result):
    try:
        if result['last_login_bupt'] == 'NULL':
            return ""
    except:
        if result.last_login_bupt != '':
            return u"(北邮" + result.last_login_bupt + u")"
        else:
            return u"(" + result.country_cn + result.province + u")"


# 获取发帖日期列表
@register.filter
def post_date(post, tp):
    return json.dumps(post[tp], ensure_ascii=False)


# 获取各类型时间发帖数量
@register.filter
def post_num(data_info, tp):
    return data_info[tp]
