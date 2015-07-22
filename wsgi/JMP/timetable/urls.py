__author__ = 'Jono'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.details, name='details'),
    url(r'^results/$', views.results, name='results'),
    url(r'^processing/$', views.processing, name='processing'),
    url(r'^download/$', views.download, name='download'),
]