from django.conf.urls import patterns, url

from temperatures import views

urlpatterns = patterns('',
                       url(r'^$', views.get_sensor_data, name='getSensorData'),
                       url(r'list', views.get_sensor_list, name='getSensorList'),
                       url(r'rooms$', views.get_rooms, name='getRooms'),
                       url(r'rooms/toggle', views.toggle_control,
                           name='toggleControl'),
                       url(r'rooms/addToTemperature', views.add_to_temperature,
                           name='addToTemperature'),
)