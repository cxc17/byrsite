# coding: utf-8

from django import template
import json

register = template.Library()


# 处理用户星座数据
@register.filter
def astro_info(data_info, gender):
    if gender == 'boy':
        data_info = data_info[u'男生']
    elif gender == 'girl':
        data_info = data_info[u'女生']
    else:
        data_info = data_info[u'全部']
    astro_data = []
    astros = [u'白羊座', u'金牛座', u'双子座', u'巨蟹座', u'狮子座', u'处女座', u'天秤座', u'天蝎座', u'射手座', u'魔羯座', u'水瓶座', u'双鱼座']
    for astro in astros:
        try:
            astro_data.append(data_info[astro])
        except:
            astro_data.append(0)
    return astro_data


# 处理用户星座比例数据
@register.simple_tag
def astro_value(data_info, gender, astro):
    if gender == 'boy':
        data_info = data_info[u'男生']
    elif gender == 'girl':
        data_info = data_info[u'女生']
    else:
        data_info = data_info[u'全部']

    return data_info[astro]


# 处理全国用户数
@register.filter
def province_value(data_info):
    province = []
    for k, v in data_info[u'全部'].items():
        province.append({'name': k, 'value': v})

    return json.dumps(province, ensure_ascii=False)


# 处理全国用户数
@register.filter
def province_info(data_info, gender):
    if gender == 'boy':
        data_info = data_info[u'男生']
    elif gender == 'girl':
        data_info = data_info[u'女生']
    else:
        data_info = data_info[u'全部']
    province_data = []
    provinces = [u'广东', u'天津', u'河北', u'上海', u'浙江', u'山东', u'江苏', u'四川', u'河南', u'陕西', u'辽宁',
                 u'山西', u'福建', u'湖北', u'安徽', u'湖南', u'黑龙江', u'江西', u'香港', u'重庆', u'吉林', u'广西', u'内蒙古',
                 u'云南', u'甘肃', u'贵州', u'海南', u'新疆', u'宁夏', u'青海', u'台湾', u'西藏', u'澳门']
    for province in provinces:
        try:
            province_data.append(data_info[province])
        except:
            province_data.append(0)
    return province_data


# 处理全世界用户数
@register.filter
def world_value(data_info):
    world = []
    for k, v in data_info[u'全部'].items():
        world.append({'name': k, 'value': v})

    return json.dumps(world, ensure_ascii=False)


# 处理北邮用户数
@register.filter
def bupt_info(data_info, gender):
    if gender == 'boy':
        data_info = data_info[u'男生']
    elif gender == 'girl':
        data_info = data_info[u'女生']
    else:
        data_info = data_info[u'全部']
    bupt_data = []
    bupts = [u"学一", u"学二", u"学三", u"学四", u"学五", u"学六", u"学八", u"学九", u"学十", u"学十一", u"学十三", u"学二十九",
             u"学十创新大本营", u"主楼", u"明光楼", u"新科研楼", u"教一", u"教二", u"教三", u"教四", u"教九", u"无线网"]
    for bupt in bupts:
        try:
            bupt_data.append(data_info[bupt])
        except:
            bupt_data.append(0)
    return bupt_data


# 获取发帖日期列表
@register.filter
def post_date(data_info, tp):
    return json.dumps(data_info[tp], ensure_ascii=False)


# 获取各类型时间发帖数量
@register.simple_tag
def post_num(data_info, tp, gender):
    if gender == 'boy':
        post_day_num = data_info[tp][u'男生']
    elif gender == 'girl':
        post_day_num = data_info[tp][u'女生']
    else:
        post_day_num = data_info[tp][u'全部']

    return post_day_num


# 获取跟帖日期列表
@register.filter
def comment_date(data_info, tp):
    return json.dumps(data_info[tp], ensure_ascii=False)


# 获取各类型时间跟帖数量
@register.simple_tag
def comment_num(data_info, tp, gender):
    if gender == 'boy':
        comment_day_num = data_info[tp][u'男生']
    elif gender == 'girl':
        comment_day_num = data_info[tp][u'女生']
    else:
        comment_day_num = data_info[tp][u'全部']

    return comment_day_num
