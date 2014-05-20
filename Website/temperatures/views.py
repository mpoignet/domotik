from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from temperatures.models import Device, Record
from django.core import serializers
import json
import datetime

# Create your views here.

def list(request):
    sensorList = Device.objects.all().values()
    startDate = request.GET.get('startDate', str((datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')))
    endDate = request.GET.get('endDate', str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    sensors = []
    for sensor in sensorList:
        s={}
        if(not sensor['name']):
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']

        s['values'] = []
        records = Record.objects.filter(device_id=sensor['id']).filter(date__gte=startDate).filter(date__lte=endDate)
        #nbRecord = 25000
        #if(records.count()>=nbRecord):
        #    records = records.order_by('date')[records.count()-nbRecord:records.count()].values()
        for record in records:
            dateString = str(record.date.strftime('%Y-%m-%d %H:%M:%S'))
            s['values'].append({'date': dateString, 'temperature': record.measure})
        sensors.append(s)   

    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")
