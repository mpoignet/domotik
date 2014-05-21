from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from temperatures.models import Device, Record
from django.core import serializers
import json
import datetime

# Create your views here.

def getList(request):
    sensorList = Device.objects.all().values()
    sensors = []
    for sensor in sensorList:
        s={}
        if(not sensor['name']):
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']
        s['id'] = sensor['id']
        sensors.append(s)   
    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")


def getData(request):
    sensorList = request.GET.getlist('sensors', [])
    if(sensorList):
        sensorList = Device.objects.filter(pk__in=sensorList).values()
    else:
        sensorList = Device.objects.all().values()
    startDate = request.GET.get('startDate', '')
    endDate = request.GET.get('endDate', '')

    sensors = []
    for sensor in sensorList:
        s={}
        if(not sensor['name']):
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']
        s['values'] = []
        if(startDate and endDate):
            records = Record.objects.filter(device_id=sensor['id']).filter(date__gte=startDate).filter(date__lte=endDate)
        elif(startDate):
            records = Record.objects.filter(device_id=sensor['id']).filter(date__gte=startDate)
        else:
            records = Record.objects.filter(device_id=sensor['id'])
            records = records.order_by('-date')[0:250]
        print startDate
        print endDate
        if(len(records) > 0):
            for record in records:
                dateString = str(record.date.strftime('%Y-%m-%d %H:%M:%S'))
                s['values'].append({'date': dateString, 'temperature': record.measure})
            sensors.append(s)   

    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")


