from rest_framework import serializers
from backend.models import Room, Sensor, Actuator, Record, Watcher

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('id', 'name', 'address')

class RoomSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer()

    class Meta:
        model = Room
        fields = ('id', 'name', 'isControlled', 'temperature', 'sensor', 'actuator')
