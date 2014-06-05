from django.conf.urls import patterns, url

from temperatures import views

urlpatterns = patterns('',
    url(r'^$', views.getSensorData, name='getSensorData'),
    url(r'list', views.getSensorList, name='getSensorList'),
    url(r'rooms$', views.getRooms, name='getRooms'),
    url(r'rooms/toggle', views.toggleControl, name='toggleControl'),
    url(r'rooms/addToTemperature', views.addToTemperature, name='addToTemperature'),
)