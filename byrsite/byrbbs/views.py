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
    # 搜索开始时间
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

    # 精确匹配结果
    result_exact = []
    for post in post_result:
        result_exact.append(post)
    for comment in comment_result:
        result_exact.append(comment)
    result_exact = sorted(result_exact, key=lambda i: i.publish_time, reverse=True)

    # 模糊匹配数目
    post_count_fuzzy = byr_post.objects.raw("SELECT id, COUNT(id) as post_count from `post` WHERE user_id like %s or "
                                            "user_name like %s ", [key+'_%', key+'_%'])[0].post_count
    comment_count_fuzzy = byr_comment.objects.raw("SELECT id, COUNT(id) as comment_count from `comment` WHERE user_id "
                                                  "like %s or user_name like %s", [key+'_%', key+'_%'])[0].comment_count
    # 匹配数目
    search_count_exact = post_count + comment_count
    search_count_fuzzy = post_count_fuzzy + comment_count_fuzzy
    search_count = search_count_exact + search_count_fuzzy
    # 结果总页数
    page_max = get_page(search_count)

    # 规范page数目
    if page <= 0:
        page = 1
    elif page > page_max:
        page = page_max





    # 模糊匹配.raw('SELECT * FROM myapp_person')
    # post_result_fuzzy = byr_post.objects.filter((Q(user_id__istartswith=key) | Q(user_name__istartswith=key)),
    #                                             ~Q(user_id=key), ~Q(user_name=key)).order_by("-publish_time")
    # post_count_fuzzy = post_result_fuzzy.count()
    # comment_result_fuzzy = byr_comment.objects.filter((Q(user_id__istartswith=key) | Q(user_name__istartswith=key)),
    #                                                   ~Q(user_id=key), ~Q(user_name=key)).order_by("-publish_time")
    # comment_count_fuzzy = comment_result_fuzzy.count()
    post_result_fuzzy = byr_post.objects.raw("SELECT * from `post` WHERE user_id like %s or user_name "
                                             "like %s order by `publish_time` desc", [key+'_%', key+'_%'])
    comment_result_fuzzy = byr_comment.objects.raw("SELECT * from `comment` WHERE user_id like %s or user_name "
                                                   "like %s order by `publish_time` desc", [key+'_%', key+'_%'])





    # 获取搜索页面的结果
    result_page_exact = get_page(search_count_exact)
    if page < result_page_exact:
        search_result = result_exact[(page-1)*10: page*10]
    elif page == result_page_exact:
        search_result = result_exact[(page-1)*10:]
        if len(search_result) < 10:
            for post in post_result_fuzzy:
                if len(search_result) < 10:
                    search_result.append(post)
                else:
                    break
        if len(search_result) < 10:
            for comment in comment_result_fuzzy:
                if len(search_result) < 10:
                    search_result.append(comment)
                else:
                    break
    else:
        if search_count_exact % 10 == 0:
            pass_count = (page - result_page_exact - 1) * 10
        else:
            pass_count = (page - result_page_exact) * 10 - search_count_exact % 10
        if pass_count <= post_count_fuzzy:
            search_result = post_result_fuzzy[pass_count: pass_count+10]
            if len(search_result) < 10:
                result = []
                for i in search_result:
                    result.append(i)
                search_result = result
                for comment in comment_result_fuzzy:
                    if len(search_result) < 10:
                        search_result.append(comment)
                    else:
                        break
        else:
            pass_count = pass_count - post_count_fuzzy
            search_result = comment_result_fuzzy[pass_count: pass_count+10]

    # 搜索结束时间
    end_time = time.time()
    search_time = end_time - start_time
    print search_time

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
