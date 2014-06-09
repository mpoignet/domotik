from django.conf.urls import patterns, url

from backend import views

urlpatterns = patterns('',
                       url(r'^$', views.get_sensor_data, name='get_sensor_data'),
                       url(r'list', views.get_sensor_list, name='get_sensor_list'),
                       url(r'rooms$', views.get_rooms, name='get_rooms'),
                       url(r'rooms/toggle', views.toggle_control,
                           name='toggle_control'),
                       url(r'rooms/addToTemperature', views.add_to_temperature,
                           name='add_to_temperature'),
)