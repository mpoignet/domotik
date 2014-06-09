from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from graphs import views


urlpatterns = patterns('',
                       url(r'^index.html$', views.index, name='index'),
                       url(r'^watchers.html$', views.watchers, name='watchers'),
                       url(r'^rooms.html$', views.rooms, name='rooms'),
                       url(r'^configure-rooms.html$', views.configureRooms,
                           name='configure-rooms'),
                       url(r'^configure-watchers.html$',
                           views.configureWatchers, name='configure-watchers'),
                       # url(r'^.html$', views.testFlot, name='testFlot'),
)

urlpatterns += staticfiles_urlpatterns()
