from django.conf.urls import patterns, url

from temperatures import views

urlpatterns = patterns('',
    url(r'^$', views.getSensorData, name='getSensorData'),
    url(r'list', views.getSensorList, name='getSensorList'),
)