from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from frontend import views


urlpatterns = patterns('',
                       url(r'^index.html$', views.index, name='index'),
                       url(r'^watchers.html$', views.watchers, name='watchers'),
                       url(r'^rooms.html$', views.rooms, name='rooms'),
                       url(r'^configure-rooms.html$', views.configure_rooms,
                           name='configure_rooms'),
                       url(r'^configure-watchers.html$',
                           views.configure_watchers, name='configure_watchers'),
                       # url(r'^.html$', views.testFlot, name='testFlot'),
)

urlpatterns += staticfiles_urlpatterns()
