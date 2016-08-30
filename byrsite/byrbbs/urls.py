from django.conf.urls import url

from views import *


urlpatterns = [
    url(r'^$', index),
    # url(r'^key=(?P<key>.+)', search)
]
