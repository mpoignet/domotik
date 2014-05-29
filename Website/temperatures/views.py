from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from temperatures.models import Sensor, Record
from django.core import serializers
from collections import OrderedDict
import json
import csv
import datetime

# Create your views here.

def getSensorList(request):
    sensorList = Sensor.objects.all().values()
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


def getSensorData(request):
    sensorList = request.GET.getlist('sensors', []) 
    if(sensorList):
        sensorList = Sensor.objects.filter(pk__in=sensorList).values()
    else:
        sensorList = Sensor.objects.all().values()
    startDate = request.GET.get('startDate', '')
    endDate = request.GET.get('endDate', '')
    output = request.GET.get('output', 'json')
    if(output=='csv'):
        return returnCSV(sensorList, startDate, endDate)
    return returnJson(sensorList, startDate, endDate)

def getRecords(sensorId, startDate, endDate):
    records = []
    if(startDate and endDate):
        records = Record.objects.filter(sensor_id=sensorId).filter(date__gte=startDate).filter(date__lte=endDate)
    elif(startDate):
        records = Record.objects.filter(sensor_id=sensorId).filter(date__gte=startDate)
    else:
        records = Record.objects.filter(sensor_id=sensorId)
        records = records.order_by('-date')[0:250]
    return records

    
def returnJson(sensorList, startDate, endDate):
    sensors = []
    for sensor in sensorList:
        s={}
        if(not sensor['name']):
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']
        s['values'] = []
        records = getRecords(sensor['id'], startDate, endDate)
        if(len(records) > 0):
            for record in records:
                dateString = str(record.date.strftime('%Y-%m-%d %H:%M:%S'))
                s['values'].append({'date': dateString, 'temperature': record.measure})
            sensors.append(s)   

    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")


def returnCSV(sensorList, startDate, endDate):

    sensors = []
    dates = {};
    for sensor in sensorList:
        if(not sensor['name']):
            sensorName = str(sensor['address'])
        else:
            sensorName = sensor['name']
        records = getRecords(sensor['id'], startDate, endDate)
        if(len(records) > 0):
            sensors.append(sensorName)
            for record in records:
                dateString = str(record.date.strftime('%Y-%m-%d %H:%M:%S'))
                if(not dateString in dates):
                   dates[dateString] = {}
                dates[dateString][sensorName] = record.measure 

    header = []
    header.append('date')
    for sensor in sorted(sensors):
        header.append(sensor)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sensors.csv"'
    writer = csv.writer(response)

    writer.writerow(header)
    dates = OrderedDict(sorted(dates.items()))
    for date in dates:
        row = [date]
        measures = OrderedDict(sorted(dates[date].items()))
        for sensor, value in measures.iteritems():
            row.append(value)
        writer.writerow(row)


    return response