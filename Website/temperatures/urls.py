from django.conf.urls import patterns, url

from temperatures import views

urlpatterns = patterns('',
    url(r'^$', views.list, name='list')
)