# coding: utf-8

from django.shortcuts import render
import time
import urllib2

from models import *


def index(request):
    if "key" in request.GET:
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

    result = byr_post.objects.filter(author_id=key).order_by("-post_time")
    search_count = result.count()

    if search_count % 10:
        page_max = search_count / 10 + 1
    else:
        page_max = search_count / 10

    if page <= 0:
        page = 1
        search_result = result[:10]
    elif page == 1:
        search_result = result[:10]
    elif page <= page_max:
        search_result = result[(page-1)*10:page*10]
    else:
        page = page_max
        search_result = result[(page_max-1)*10:]

    end_time = time.time()
    search_time = end_time - start_time

    return render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                  "search_result": search_result, "page_max": page_max,
                                                  "search_count": search_count})


def user(request):
    uid = request.GET.get("uid")

    url = "https://bbs.byr.cn/user/query/%s.json" % uid
    r = urllib2.Request(url, headers={'cookie': 'nforum[UTMPUSERID]=oneseven; nforum[UTMPKEY]=94340691; nforum[UTMPNUM]=3185; nforum[PASSWORD]=psGXiAucyq0F3aa9j0ds1w%3D%3D; Hm_lvt_38b0e830a659ea9a05888b924f641842=1473085151; Hm_lpvt_38b0e830a659ea9a05888b924f641842=1473335368; nforum[XWJOKE]=hoho',
                                      'x-requested-with': 'XMLHttpRequest'})
    a = urllib2.urlopen(r).read().decode("gbk")
    print a

    return render(request, 'byrbbs/user_info.html')
