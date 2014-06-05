from django.shortcuts import render
from django.template import RequestContext, loader, Template
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.http import HttpResponse
from temperatures.models import Sensor, Record, Room
from django.core import serializers
from collections import OrderedDict
from django.forms.models import model_to_dict
import json
import csv
import datetime
import calendar
import pytz


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
    if(output=='flot'):
        return returnFlot(sensorList, startDate, endDate)
    if(output=='morris'):
        return returnMorris(sensorList, startDate, endDate)
    return returnJson(sensorList, startDate, endDate)

def getRecords(sensorId, startDate, endDate):
    if(startDate):
        startDate = datetime.datetime.fromtimestamp(int(startDate), pytz.timezone('CET')).strftime('%Y-%m-%d %H:%M:%S')
    if(endDate): 
        endDate = datetime.datetime.fromtimestamp(int(endDate), pytz.timezone('CET')).strftime('%Y-%m-%d %H:%M:%S')
    records = []
    if(startDate and endDate):
        print "DATES"
        print startDate
        print endDate
        records = Record.objects.filter(sensor_id=sensorId).filter(date__gte=startDate).filter(date__lte=endDate)
        print sensorId
        print records
    elif(startDate):
        records = Record.objects.filter(sensor_id=sensorId).filter(date__gte=startDate)
    else:
        records = Record.objects.filter(sensor_id=sensorId).order_by('-date')[0:250]
    return records

def returnMorris(sensorList, startDate, endDate):
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

    elements = []
    for date in dates:
        element = {'date': date}
        for sensor in dates[date]:
            element[sensor] = dates[date][sensor]
        elements.append(element)

    return HttpResponse(json.dumps({'mElements': elements}), content_type="application/json")


def returnFlot(sensorList, startDate, endDate):
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
                # javascript timestamps are in ms, unix timestamp in s, hence the *1000
                timestamp = calendar.timegm(record.date.timetuple())*1000
                s['values'].append((timestamp, record.measure))
            sensors.append(s)   

    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")

    
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

def getRooms(request):
    if request.method == 'GET':
        rooms=[]
        for room in Room.objects.all():
            roomDict = model_to_dict(room)
            if(room.sensor):
                roomDict['sensor'] = model_to_dict(room.sensor)
                record = Record.objects.filter(sensor_id=room.sensor.id).order_by('-date')[0]
                roomDict['lastMeasure'] = {'date': str(record.date.strftime('%Y-%m-%d %H:%M:%S')), 'measure': record.measure}
            rooms.append(roomDict)
        return HttpResponse(json.dumps({'rooms': rooms}), content_type="application/json")
    elif request.method == 'POST':
        roomName = request.POST.get('name')
        sensorId = request.POST.get('id')
        room = Room(name=roomName, sensor_id=sensorId)
        room.save();
        newRoom = Room.objects.get(id=room.id)
        c = RequestContext(request,{'room': json.dumps(model_to_dict(newRoom))})
        t = Template("{% autoescape off %}{{room}}{% endautoescape %} ") # A dummy template
        response = HttpResponse(t.render(c), mimetype = u'application/json')
        return response

def toggleControl(request):
    roomId = request.POST.get('id')
    room = Room.objects.get(id=roomId)
    if(room.isControlled):
        room.isControlled = False
    else:
        room.isControlled = True
    
    room.save()
    return HttpResponse(json.dumps(room.isControlled), content_type="application/json")

def addToTemperature(request):
    roomId = request.POST.get('id')
    deltaT = request.POST.get('t')
    room = Room.objects.get(id=roomId)
    room.temperature = room.temperature + int(deltaT)
    room.save()
    return HttpResponse(json.dumps(room.temperature), content_type="application/json")