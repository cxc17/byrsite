from django.shortcuts import render
from django.http import HttpResponse

from models import *


def fun(request):
    m = board

    a = m.objects.all()

    return render(request, 'byrbbs/index.html', {'a': a[0].board_name})
