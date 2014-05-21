from django.conf.urls import patterns, url

from temperatures import views

urlpatterns = patterns('',
    url(r'^$', views.getData, name='getData'),
    url(r'list', views.getList, name='getList'),
)