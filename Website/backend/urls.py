from django.conf.urls import patterns, url

from backend import views

urlpatterns = patterns('',
                       url(r'^records$', views.handle_records, name='handle_records'),
                       url(r'^sensors', views.get_sensor_list, name='get_sensor_list'),
                       url(r'^rooms$', views.get_rooms, name='get_rooms'),
                       url(r'^rooms/toggle', views.toggle_control,
                           name='toggle_control'),
                       url(r'^rooms/addToTemperature', views.add_to_temperature,
                           name='add_to_temperature'),
)