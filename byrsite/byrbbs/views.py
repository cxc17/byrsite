from django.shortcuts import render
from django.http import HttpResponse

from models import *


def index(request):
    return render(request, 'byrbbs/index.html')


def search(request):
    m = board
    a = m.objects.all()

    return HttpResponse("ok")
