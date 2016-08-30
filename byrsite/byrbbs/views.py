from django.shortcuts import render
from django.http import HttpResponse

from models import *


def index(request):
    if "key" in request.GET:
        return render(request, 'byrbbs/search.html')

    return render(request, 'byrbbs/index.html')


# def search(request, key=None):
#     m = board
#     a = m.objects.all()
#
#     return HttpResponse(key)
