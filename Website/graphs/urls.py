from django.conf.urls import patterns, url

from graphs import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)