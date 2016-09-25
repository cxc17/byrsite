# coding: utf-8

from django import template


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
    # return "处女座"
