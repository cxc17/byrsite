from django.conf.urls import url

from views import *


urlpatterns = [
    url(r'^$', index),
    url(r'^user$', user),
    url(r'^data$', data),
    url(r'^data_astro$', data_astro)
]
