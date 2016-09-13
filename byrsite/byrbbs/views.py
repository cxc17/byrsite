# coding: utf-8

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
import time
import urllib2
import json

from models import *


def index(request):
    if "key" in request.GET and request.GET.get("key") != "":
        return search(request)

    return render(request, 'byrbbs/index.html')


def search(request):
    start_time = time.time()

    # 获取参数
    key = request.GET.get("key")
    if "p" in request.GET:
        try:
            page = int(request.GET.get("p"))
        except:
            page = 1
    else:
        page = 1

    # 精确匹配
    post_result = byr_post.objects.filter(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
    post_count = post_result.count()
    comment_result = byr_comment.objects.filter(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
    comment_count = comment_result.count()

    # 模糊匹配
    # post_result_fuzzy = byr_post.objects.filter(Q(user_id__istartswith=key) | Q(user_name__istartswith=key))\
    #     .exclude(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
    # post_count_fuzzy = post_result_fuzzy.count()
    # comment_result_fuzzy = byr_comment.objects.filter(Q(user_id__istartswith=key) | Q(user_name__istartswith=key))\
    #     .exclude(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
    # comment_count_fuzzy = comment_result_fuzzy.count()

    # 匹配数目
    search_count_exact = post_count + comment_count
    # search_count_fuzzy = post_count_fuzzy + comment_count_fuzzy
    search_count = search_count_exact #+ search_count_fuzzy

    # 结果总页数
    page_max = get_page(search_count)

    # 规范page数目
    if page <= 0:
        page = 1
    elif page > page_max:
        page = page_max

    # 搜索结果
    result = []
    # 精确匹配结果
    for post in post_result:
        result.append(post)
    for comment in comment_result:
        result.append(comment)

    result = sorted(result, key=lambda i: i.publish_time, reverse=True)

    # # 模糊匹配结果
    # for post in post_result_fuzzy:
    #     result.append(post)
    # for comment in comment_result_fuzzy:
    #     result.append(comment)

    if page <= 0:
        search_result = result[:10]
    elif page == 1:
        search_result = result[:10]
    elif page <= page_max:
        search_result = result[(page-1)*10:page*10]
    else:
        search_result = result[(page_max-1)*10:]

    end_time = time.time()
    search_time = end_time - start_time

    return render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                  "search_result": search_result, "page_max": page_max,
                                                  "search_count": search_count})


def user(request):
    user_id = request.GET.get("uid")
    user_info = byr_user.objects.filter(user_id=user_id)

    try:
        user_info = user_info[0]
    except:
        url = "https://bbs.byr.cn/user/query/%s.json" % user_id
        req = urllib2.Request(url, headers={'cookie': 'nforum[UTMPUSERID]=oneseven; nforum[PASSWORD]=psGXiAucyq0F3aa9j0ds1w%3D%3D;',
                                            'x-requested-with': 'XMLHttpRequest'})
        info = urllib2.urlopen(req).read()
        try:
            user_info = info.decode("gbk")
        except:
            user_info = info

        try:
            user_info = json.loads(user_info)
            if user_info["gender"] == u'm':
                user_info["gender"] = u'男生'
            elif user_info["gender"] == u'f':
                user_info["gender"] = u'女生'
            else:
                user_info["gender"] = u'保密'
            user_info["last_login_time"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(user_info["last_login_time"])))
            user_info["status"] = user_info["status"].split(u"，")[0]
        except:
            return HttpResponse('查无此人')

    return render(request, 'byrbbs/userInfo.html', {'user_info': user_info, 'user_id': user_id})


# 获取页数
def get_page(count):
    if count % 10:
        return count / 10 + 1
    else:
        return count / 10
