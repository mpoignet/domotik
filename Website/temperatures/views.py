from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from temperatures.models import Device, Record
from django.core import serializers
import json

# Create your views here.

def list(request):
    sensorList = Device.objects.all().values()

    sensors = []
    for sensor in sensorList:
        s={}
        if(not sensor['name']):
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']

        s['values'] = []
        records = Record.objects.filter(device_id=sensor['id']).values()
        for record in records:
            dateString = str(record['date'].strftime('%Y-%m-%d %H:%M:%S'))
            s['values'].append({'date': dateString, 'temperature': record['measure']})
        sensors.append(s)

    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")
