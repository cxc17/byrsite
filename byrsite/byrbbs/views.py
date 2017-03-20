# coding: utf-8

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from collections import defaultdict
from math import log
import time
import urllib2
import json
import jieba
import re

from models import *


def index(request):
    if "key" in request.GET:
        if request.GET.get("key").strip() != "":
            web_type = request.GET.get("type")
            if not web_type:
                try:
                    web_type = request.COOKIES["type"]
                except:
                    web_type = 'all'
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

            if web_type == 'all' and search_type == 'all' and web_date == 'all':
                return search_all(request)
            else:
                return search(request)
        else:
            return HttpResponseRedirect('/byrbbs')

    return render(request, 'byrbbs/index.html')


def search_all(request):
    # 搜索开始时间
    start_time = time.time()

    # 获取页数参数
    key = request.GET.get("key").strip()
    if "p" in request.GET:
        try:
            page = int(request.GET.get("p"))
        except:
            page = 1
    else:
        page = 1
    # 获取类型参数
    web_type = 'all'
    # 获取搜索类型参数
    search_type = "all"
    # 获取时间参数
    web_date = "all"

    # 停用词
    stop_word = byr_stop_word.objects.filter(Q(id=2742))[0].word

    seg = ur"[\s\.\!\/\"\'\-\|\]\[\{\}\\]+|[ⅹⅸⅷⅶⅵⅴⅳⅲⅱⅰ℡№℉℃‵″′‰‥‘яюэьыъщшчцхфутсрпонмлкйизжеёдгвбаωψχφυτσρποξνμλκιθηζεδγβαˋˊˉˇ÷×±°¨§￤￢￡￠｀＿＾ｚｙｘｗｖｕｔｓｒｑｐｏｎｍｌｋｊｉｈｇｆｅｄｃｂａ＠＞＝＜９８７６５４３２１０＋＊＇＆％＄＃﹫﹪﹦﹥﹤﹣﹢﹡﹠﹟﹞﹝﹜﹛﹚﹙﹗﹖﹕﹔﹒﹐﹍﹌﹋﹊﹉﹄﹂﹁﹀︾︽︺︹︸︷︴︰——！，。：、~@#￥%……&*（）；－):ǔūúüùɡǎāáàěêéёèēīìíǐōòóǒňǹńǖǘǚǜ①②③④⑤⑥⑦⑧⑨⑩⑴⑵⑶⑷⑸⑹⑺─┅┆┈┍┎┒┙├┝┟┣┫┮┰┱┾┿╃╄╆╈╋▉▲▼※Ⅱ←→↖↗↘↙《》┊┋┇┉┠┨┌┐┑└┖┘┚┤┥┦┏┓┗┛┯┷┻┳┃━〓¤`˙⊙│〉〈⒂～？．＂”“’·■／￣�︱〕〔【】』『」「◎○◆●☉　┬┴┸┼═╔╗╚╝╩╭╮╯╰╱╲▁▅▆▇█▊▌▍▎▓▕□▽◇◢◣◤◥★☆︶︻︼︵︿﹃﹎﹏△▔▏▋▄▃▂△▔▏▋▄▃▂╳╬╫╪╨╧╦╥╣╢╠╟╜╙╘╖╓║╅╂┭┕┄〞〝〗〖〒〇〃⿻⿺⿹⿸⿷⿵⿴⿲]+"
    key = re.sub(seg, " ".decode("utf8"), key)
    key_infos = list(jieba.cut(key))
    try:
        key_infos.remove(u" ")
    except:
        pass
    key_info = []
    key_info_stop = []
    for i in key_infos:
        if i in stop_word:
            key_info_stop.append(i)
        else:
            key_info.append(i)
    post_index = byr_index.objects.raw("select id, doc_fre, list from post_index where word in (\"%s\")"
                                       % "\",\"".join(key_info))
    all_index = defaultdict(int)
    for index in post_index[:5]:
        index_list = str(index.list)
        try:
            index_list = json.loads(index_list)
        except:
            index_list = index_list.replace(",,", ",")
            index_list = json.loads(index_list)
        # import re
        # index_list = re.split(r",|:", index.list)
        index_IDF = int(log(400000/index.doc_fre))
        # for i in xrange(0, len(index_list), 2):
        #     all_index[index_list[i]] += index_IDF * int(index_list[i+1])
        for k, v in index_list.items():
            all_index[k] += index_IDF * v
    if len(all_index) == 0:
        post_index = byr_index.objects.raw("select id, doc_fre, list from post_index where word in (\"%s\")"
                                           % "\",\"".join(key_info_stop))
        for index in post_index:
            index_list = json.loads(str(index.list))
            index_IDF = int(log(400000/index.doc_fre))
            for k, v in index_list.items():
                all_index[k] += index_IDF * v
            if len(all_index) != 0:
                break

    # 内容匹配数目
    search_count_content = len(all_index)

    # 精确匹配数目
    try:
        post_count = byr_user.objects.filter(Q(user_id=key) | Q(user_name=key))[0].post_num
    except:
        post_count = 0
    try:
        comment_count = byr_user.objects.filter(Q(user_id=key) | Q(user_name=key))[0].comment_num
    except:
        comment_count = 0

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
    search_count = search_count_exact + search_count_fuzzy + search_count_content

    # 结果总页数
    page_max = get_page(search_count)[0]

    # 规范page数目
    if page <= 0:
        page = 1
    elif page > page_max:
        page = page_max

    # 结果匹配页数
    content_page_max = get_page(search_count_content)[0]

    # 精确匹配页数
    result_page_exact, search_result_exact_last = get_page(search_count_content + search_count_exact)

    # 当搜索页面在结果查找之内
    if page < content_page_max:
        all_index = sorted(all_index.items(), key=lambda x: x[1], reverse=True)
        search_post_id = []
        for index in all_index[(page-1)*10:page*10]:
            search_post_id.append(index[0])
        search_result = byr_post.objects.raw("SELECT *from post where id in (\"%s\")" % "\",\"".join(search_post_id))
        # 搜索结束时间
        end_time = time.time()
        search_time = end_time - start_time
        response = render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                          "search_result": search_result, "page_max": page_max,
                                                          "search_count": search_count, "type": web_type,
                                                          "date": web_date, 'search_type': search_type})

        response.set_cookie('type', 'all')
        return response
    post_result = byr_post.objects.filter(Q(user_id=key) | Q(user_name=key))
    comment_result = byr_comment.objects.filter(Q(user_id=key) | Q(user_name=key))
    # 当搜索页面等于结果查找
    if page == content_page_max:
        all_index = sorted(all_index.items(), key=lambda x: x[1], reverse=True)
        search_post_id = []
        for index in all_index[(page-1)*10:]:
            search_post_id.append(index[0])
        search_result = []
        search_result.extend(byr_post.objects.raw("SELECT *from post where id in (\"%s\")" % "\",\"".join(search_post_id)))
        if len(search_result) < 10:
            # 精确匹配结果
            search_result.extend(post_result[:10-len(search_result)])
            if len(search_result) < 10:
                search_result.extend(comment_result[:10-len(search_result)])
    # 当搜索页面在精确查找之内
    elif page < result_page_exact:
        search_result = []
        start_num = 10 - len(all_index) % 10
        search_result.extend(post_result[start_num:start_num+10])
        if len(search_result) < 10:
            search_result.extend(comment_result[:10-len(search_result)])
    # 当搜索页面为精确查找页数
    elif page == result_page_exact:
        last_num = 10 - len(all_index) % 10
        search_count_exact -= last_num
        start_num = search_count_exact % 10
        # 精确匹配结果
        search_result = []
        search_result.extend(comment_result[max(0, comment_count-start_num):comment_count])
        if len(search_result) < 10:
            search_result.extend(post_result[max(0, post_count-(start_num-len(search_result))):post_count])
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

    response = render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                      "search_result": search_result, "page_max": page_max,
                                                      "search_count": search_count, "type": web_type,
                                                      "date": web_date, 'search_type': search_type})
    response.set_cookie('type', 'all')
    return response


def search(request):
    # 搜索开始时间
    start_time = time.time()

    # 获取页数参数
    key = request.GET.get("key").strip()
    if "p" in request.GET:
        try:
            page = int(request.GET.get("p"))
        except:
            page = 1
    else:
        page = 1
    # 获取类型参数
    web_type = "user"
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

    # 用户匹配
    user_info = byr_user.objects.filter(Q(user_id=key) | Q(user_name=key))
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
        search_count += user_info.count()
        response = render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                          "search_result": search_result, 'user_info': user_info,
                                                          "search_count": search_count, 'search_type': search_type,
                                                          "type": web_type, "date": web_date, "page_max": page_max})

        response.set_cookie('type', 'user')
        return response
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
    search_count += user_info.count()
    response = render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                      "search_result": search_result, 'user_info': user_info,
                                                      "page_max": page_max, "search_count": search_count,
                                                      "type": web_type, "date": web_date, 'search_type': search_type})
    response.set_cookie('type', 'user')
    return response


def search_exact(request, key, page, web_type, search_type, web_date, start_time):
    if web_date == 'all':
        web_strftime = 0
    else:
        web_localtime = time.time() - 86400*int(web_date)
        web_strftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(web_localtime))
    # 用户匹配
    user_info = byr_user.objects.filter(Q(user_id=key) | Q(user_name=key))

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
        page = max(1, page_max)

    # 精确匹配结果
    result_exact = []
    result_exact.extend(post_result[:page*10])
    result_exact.extend(comment_result[:page*10])
    result_exact = sorted(result_exact, key=lambda i: i.publish_time, reverse=True)

    search_result = result_exact[(page-1)*10: page*10]

    # 搜索结束时间
    end_time = time.time()
    search_time = end_time - start_time
    search_count += user_info.count()
    response = render(request, 'byrbbs/search.html', {"key": key, "page": page, "search_time": search_time,
                                                      "search_result": search_result, 'user_info': user_info,
                                                      "page_max": page_max, "search_count": search_count,
                                                      "type": web_type, "date": web_date, 'search_type': search_type})
    response.set_cookie('type', 'user')
    return response


def user(request):
    user_id = request.GET.get("uid")
    user_info = byr_user.objects.filter(user_id=user_id)

    try:
        user_info = user_info[0]
    except:
        url = "https://bbs.byr.cn/user/query/%s.json" % user_id
        req = urllib2.Request(url, headers={'cookie': 'nforum[UTMPUSERID]=byrdata; nforum[PASSWORD]=POtvs%2BkhqgVoWBVTalh2VA%3D%3D;',
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
            user_info["last_login_bupt"] = 'NULL'
            user_info["post_num"] = 0
            user_info["comment_num"] = 0
            return render(request, 'byrbbs/userInfo.html', {'user_info': user_info, 'user_id': user_id})
        except:
            return HttpResponse('查无此人')

    post_result = byr_post.objects.raw("SELECT id, publish_time from post where user_id=%s order by publish_time", [user_id])
    try:
        last_post = byr_post.objects.raw("SELECT id, url, title from post where user_id=%s order by publish_time desc "
                                         "limit 1", [user_id])[0]
        count = 0
        post_date_num = [0]
        post_date = ["2004/05/28"]
        post_year_num = [0]*14
        post_month_num = [0]*12
        post_day_num = [0]*31
        post_weekday_num = [0]*7
        post_hour_num = [0]*24
        for i in post_result:
            cdatetime = i.publish_time
            cdate = str(cdatetime.date()).replace("-", "/")
            cyear = cdatetime.year-2004
            cmonth = cdatetime.month-1
            cday = cdatetime.day-1
            cweekday = cdatetime.weekday()
            chour = cdatetime.hour

            # 日期
            if cdate == post_date[count]:
                post_date_num[count] += 1
            else:
                post_date.append(cdate)
                post_date_num.append(1)
                count += 1
            post_year_num[cyear] += 1
            post_month_num[cmonth] += 1
            post_day_num[cday] += 1
            post_weekday_num[cweekday] += 1
            post_hour_num[chour] += 1

        post = {"post_date": post_date, "post_date_num": post_date_num, "post_year_num": post_year_num,
                "post_month_num": post_month_num, "post_day_num": post_day_num, "post_weekday_num": post_weekday_num,
                "post_hour_num": post_hour_num}
    except:
        last_post = ''
        post = ''

    comment_result = byr_comment.objects.raw("SELECT id, publish_time from comment where user_id=%s order by "
                                             "publish_time", [user_id])
    try:
        last_comment = byr_post.objects.raw("SELECT id, url, title from comment where user_id=%s order by publish_time "
                                            "desc limit 1", [user_id])[0]
        count = 0
        comment_date_num = [0]
        comment_date = ["2004/05/28"]
        comment_year_num = [0]*14
        comment_month_num = [0]*12
        comment_day_num = [0]*31
        comment_weekday_num = [0]*7
        comment_hour_num = [0]*24
        for i in comment_result:
            cdatetime = i.publish_time
            cdate = str(cdatetime.date()).replace("-", "/")
            cyear = cdatetime.year-2004
            cmonth = cdatetime.month-1
            cday = cdatetime.day-1
            cweekday = cdatetime.weekday()
            chour = cdatetime.hour

            # 日期
            if cdate == comment_date[count]:
                comment_date_num[count] += 1
            else:
                comment_date.append(cdate)
                comment_date_num.append(1)
                count += 1
            comment_year_num[cyear] += 1
            comment_month_num[cmonth] += 1
            comment_day_num[cday] += 1
            comment_weekday_num[cweekday] += 1
            comment_hour_num[chour] += 1
        comment = {"comment_date": comment_date, "comment_date_num": comment_date_num, "comment_year_num": comment_year_num,
                   "comment_month_num": comment_month_num, "comment_day_num": comment_day_num,
                   "comment_weekday_num": comment_weekday_num, "comment_hour_num": comment_hour_num}
    except:
        last_comment = ''
        comment = ''

    return render(request, 'byrbbs/userInfo.html', {'user_info': user_info, 'user_id': user_id, 'comment': comment,
                                                    'post': post, "last_post": last_post, 'last_comment': last_comment})


def data(request):
    try:
        data_name = request.GET.get("did")
    except:
        data_name = ""

    if data_name in ['astro', 'china', 'world', 'bupt', 'introduce', 'post', 'comment']:
        try:
            data_info = byr_data.objects.filter(data_name=data_name)
            data_info = json.loads(data_info[0].data_value)
        except:
            data_info = ""
        if data_name == 'astro':
            return render(request, 'byrbbs/data_type/data_astro.html', {'data_info': data_info})
        elif data_name == 'china':
            return render(request, 'byrbbs/data_type/data_china.html', {'data_info': data_info})
        elif data_name == 'world':
            return render(request, 'byrbbs/data_type/data_world.html', {'data_info': data_info})
        elif data_name == 'bupt':
            return render(request, 'byrbbs/data_type/data_bupt.html', {'data_info': data_info})
        elif data_name == 'post':
            return render(request, 'byrbbs/data_type/data_post.html', {'data_info': data_info})
        elif data_name == 'comment':
            return render(request, 'byrbbs/data_type/data_comment.html', {'data_info': data_info})
        elif data_name == 'introduce':
            import datetime
            data_info = datetime.date.today()
            return render(request, 'byrbbs/data_type/data_introduce.html', {'data_info': data_info})

    return render(request, 'byrbbs/data.html')


# 获取页数
def get_page(count):
    if count % 10:
        return count / 10 + 1, count % 10
    else:
        return count / 10, 0


def verify(request):
    return HttpResponse('63633e2e1ada5f1d0045ef5b09364cdf')


def robots(request):
    return HttpResponse('User-agent: * \n')


def google_verify(request):
    return HttpResponse('google-site-verification: googlec6d197596a78ca84.html')
