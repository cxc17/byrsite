# coding: utf-8

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from collections import defaultdict
import time
import urllib2
import json

from models import *


def index(request):
    if "key" in request.GET:
        if request.GET.get("key").strip() != "":
            return search(request)
        else:
            return HttpResponseRedirect('/byrbbs')

    return render(request, 'byrbbs/index.html')


def search(request):
    # 搜索开始时间
    start_time = time.time()

    # 获取页数参数
    key = request.GET.get("key")
    if "p" in request.GET:
        try:
            page = int(request.GET.get("p"))
        except:
            page = 1
    else:
        page = 1
    # 获取类型参数
    try:
        web_type = request.GET.get("type")
    except:
        web_type = "all"
    if web_type not in ['all', 'user', 'data']:
        web_type = "all"
    # 获取搜索类型参数
    try:
        search_type = request.GET.get("search_type")
    except:
        search_type = "all"
    if search_type not in ['all', 'exact']:
        search_type = "all"
    # 获取时间参数
    try:
        web_date = request.GET.get("date")
    except:
        web_date = "all"
    if web_date not in ['all', '1', '7', '30', '365']:
        web_date = "all"

    # 搜索类型为精确匹配
    if search_type == 'exact':
        return search_exact(request, key, page, web_type, search_type, web_date, start_time)

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
    page_max = get_page(search_count)[0]

    # 规范page数目
    if page <= 0:
        page = 1
    elif page > page_max:
        page = page_max

    # 精确匹配页数
    result_page_exact, search_result_exact_last = get_page(search_count_exact)

    # 当搜索页面在精确查找之内
    if page < result_page_exact:
        # 精确匹配结果
        result_exact = []
        result_exact.extend(post_result[:page*10])
        result_exact.extend(comment_result[:page*10])
        result_exact = sorted(result_exact, key=lambda i: i.publish_time, reverse=True)

        search_result = result_exact[(page-1)*10: page*10]

        # 搜索结束时间
        end_time = time.time()
        search_time = end_time - start_time
        return render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                      "search_result": search_result, "page_max": page_max,
                                                      "search_count": search_count, "type": web_type,
                                                      "date": web_date, 'search_type': search_type})
    # 当搜索页面为精确查找页数
    if page == result_page_exact:
        # 精确匹配结果
        result_exact = []
        if page == 1:
            result_exact.extend(post_result)
            result_exact.extend(comment_result)
        else:
            result_exact.extend(post_result[max(post_count-search_result_exact_last, 0):])
            result_exact.extend(comment_result[max(comment_count-search_result_exact_last, 0):])
        result_exact = sorted(result_exact, key=lambda i: i.publish_time, reverse=True)

        search_result = result_exact[-search_result_exact_last:]
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
                for i in xrange(0, comment.comment_num):
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
    # 当搜索页面在精确查找之外
    else:
        if search_count_exact % 10 == 0:
            pass_count = (page - result_page_exact - 1) * 10
        else:
            pass_count = (page - result_page_exact) * 10 - search_count_exact % 10

        if pass_count <= post_count_fuzzy:
            search_result_count = 0
            # post模糊匹配
            post_sql = defaultdict(int)
            for post in post_count_fuzzy_tmp:
                start = 0
                for i in xrange(0, post.post_num):
                    if pass_count > 0:
                        start += 1
                        pass_count -= 1
                    elif search_result_count < 10:
                        post_sql[(post.user_id, start)] += 1
                        search_result_count += 1
                    else:
                        break
                if search_result_count == 10:
                    break

            search_result = []
            for k, v in post_sql.items():
                fuzzy_post_result = byr_post.objects.filter(user_id=k[0]).order_by("-publish_time")
                search_result.extend(fuzzy_post_result[k[1]:k[1]+v])

            # comment模糊匹配
            comment_sql = defaultdict(int)
            if search_result_count < 10:
                for comment in comment_count_fuzzy_tmp:
                    for i in xrange(0, comment.comment_num):
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
            pass_count = pass_count - post_count_fuzzy

            search_result_count = 0
            # post模糊匹配
            comment_sql = defaultdict(int)
            for comment in comment_count_fuzzy_tmp:
                start = 0
                for i in xrange(0, comment.comment_num):
                    if pass_count > 0:
                        start += 1
                        pass_count -= 1
                    elif search_result_count < 10:
                        comment_sql[(comment.user_id, start)] += 1
                        search_result_count += 1
                    else:
                        break
                if search_result_count == 10:
                    break

            search_result = []
            for k, v in comment_sql.items():
                fuzzy_comment_result = byr_comment.objects.filter(user_id=k[0]).order_by("-publish_time")
                search_result.extend(fuzzy_comment_result[k[1]:k[1]+v])

    # 搜索结束时间
    end_time = time.time()
    search_time = end_time - start_time

    return render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                  "search_result": search_result, "page_max": page_max,
                                                  "search_count": search_count, "type": web_type,
                                                  "date": web_date, 'search_type': search_type})


def search_exact(request, key, page, web_type, search_type, web_date, start_time):
    if web_date == 'all':
        web_strftime = 0
    else:
        web_localtime = time.time() - 86400*int(web_date)
        web_strftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(web_localtime))

    # 精确匹配数目
    if web_strftime:
        post_result = byr_post.objects.raw("SELECT * from (SELECT * from post WHERE user_name=%s or user_id=%s ORDER BY"
                                           " publish_time desc) c WHERE publish_time > %s", [key, key, web_strftime])
        post_count = len([i for i in post_result])
        comment_result = byr_comment.objects.raw("SELECT * from (SELECT * from comment WHERE user_name=%s or user_id=%s"
                                                 " ORDER BY publish_time desc ) c WHERE publish_time > %s", [key, key, web_strftime])
        comment_count = len([i for i in comment_result])
    else:
        post_result = byr_post.objects.filter(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
        post_count = post_result.count()
        comment_result = byr_comment.objects.filter(Q(user_id=key) | Q(user_name=key)).order_by("-publish_time")
        comment_count = comment_result.count()

    # 匹配总数目
    search_count = post_count + comment_count

    # 结果总页数
    page_max = get_page(search_count)[0]

    # 规范page数目
    if page <= 0:
        page = 1
    elif page > page_max:
        page = page_max

    # 精确匹配结果
    result_exact = []
    result_exact.extend(post_result[:page*10])
    result_exact.extend(comment_result[:page*10])
    result_exact = sorted(result_exact, key=lambda i: i.publish_time, reverse=True)

    search_result = result_exact[(page-1)*10: page*10]

    # 搜索结束时间
    end_time = time.time()
    search_time = end_time - start_time
    return render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                  "search_result": search_result, "page_max": page_max,
                                                  "search_count": search_count, "type": web_type,
                                                  "date": web_date, 'search_type': search_type})


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


def data(request):
    data_name = request.GET.get("did")
    data_info = byr_data.objects.filter(data_name=data_name)
    data_info = json.loads(data_info[0].data_value)
    return render(request, 'byrbbs/data.html', {'data_info': data_info})


# 获取页数
def get_page(count):
    if count % 10:
        return count / 10 + 1, count % 10
    else:
        return count / 10, 0
