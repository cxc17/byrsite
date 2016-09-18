# coding: utf-8

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from collections import defaultdict
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

    # 精确匹配数目
    post_result = byr_post.objects.filter(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
    post_count = post_result.count()
    comment_result = byr_comment.objects.filter(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
    comment_count = comment_result.count()

    # 模糊匹配数目
    post_count_fuzzy_tmp = byr_post.objects.raw("SELECT id, user_id, post_num from `user` where (user_id like %s or "
                                                "user_name like %s) and post_num > 0 order by user_id", [key+'_%', key+'_%'])
    post_count_fuzzy = sum(i.post_num for i in post_count_fuzzy_tmp)
    comment_count_fuzzy_tmp = byr_comment.objects.raw("SELECT id, user_id, comment_num from `user` where user_id like "
                                                      "%s or user_name like %s and comment_num > 0 order by user_id", [key+'_%', key+'_%'])
    comment_count_fuzzy = sum(i.comment_num for i in comment_count_fuzzy_tmp)

    # 匹配总数目
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

    # 精确匹配页数
    result_page_exact = get_page(search_count_exact)

    # 当搜索页面在精确查找之内
    if page < result_page_exact:
        # 精确匹配结果
        result_exact = []
        result_exact.extend(post_result)
        result_exact.extend(comment_result)
        result_exact = sorted(result_exact, key=lambda i: i.publish_time, reverse=True)

        search_result = result_exact[(page-1)*10: page*10]

        # 搜索结束时间
        end_time = time.time()
        search_time = end_time - start_time
        return render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                      "search_result": search_result, "page_max": page_max,
                                                      "search_count": search_count})



    # 模糊匹配
    post_result_fuzzy = byr_post.objects.raw("SELECT * from `post` WHERE user_id like %s or user_name "
                                             "like %s order by `publish_time` desc", [key+'_%', key+'_%'])
    comment_result_fuzzy = byr_comment.objects.raw("SELECT * from `comment` WHERE user_id like %s or user_name "
                                                   "like %s order by `publish_time` desc", [key+'_%', key+'_%'])

    if page == result_page_exact:
        # 精确匹配结果
        result_exact = []
        result_exact.extend(post_result)
        result_exact.extend(comment_result)
        result_exact = sorted(result_exact, key=lambda i: i.publish_time, reverse=True)

        search_result = result_exact[(page-1)*10:]
        search_result_count = len(search_result)

        # post模糊匹配
        post_sql = defaultdict(int)
        if search_result_count < 10:
            for post in post_count_fuzzy_tmp:
                for i in xrange(0, post.post_num):
                    if search_result_count < 10:
                        post_sql[post.user_id] += 1
                        search_result_count += 1
                    else:
                        break
                if search_result_count == 10:
                    break
            for k, v in post_sql.items():
                fuzzy_post_result = byr_post.objects.filter(user_id=k).order_by("-publish_time")
                search_result.extend(fuzzy_post_result[:v])

        # comment模糊匹配
        comment_sql = defaultdict(int)
        if search_result_count < 10:
            for comment in comment_count_fuzzy_tmp:
                for i in xrange(0, comment.post_num):
                    if search_result_count < 10:
                        comment_sql[comment.user_id] += 1
                        search_result_count += 1
                    else:
                        break
                if search_result_count == 10:
                    break
            for k, v in comment_sql.items():
                fuzzy_comment_result = byr_comment.objects.filter(user_id=k).order_by("-publish_time")
                search_result.extend(fuzzy_comment_result[:v])
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
