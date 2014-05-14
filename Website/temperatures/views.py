from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from temperatures.models import Data
import json

# Create your views here.

# def list(request):
#     latest_temperatures_list = Data.objects.all()
#     latest_temperatures_list = latest_temperatures_list.order_by('date')[latest_temperatures_list.count()-6:latest_temperatures_list.count()-1]

#     context = {'latest_temperatures_list': latest_temperatures_list}

#     template = loader.get_template('temperatures/list.html')
#     context = RequestContext(request, {
#         'latest_temperatures_list': latest_temperatures_list,
#     })

#     return render(request, 'temperatures/list.html', context)


def list(request):
    latest_temperatures_list = Data.objects.all()
    latest_temperatures_list = latest_temperatures_list.order_by('date')[latest_temperatures_list.count()-240:latest_temperatures_list.count()-1].values()
    
    sensors = []

    for key in latest_temperatures_list[0]:
        if(key != 'id' and key != 'date' and key != 'c0'):
            sensors.append({'name': key, 'values': []})



    
    for t in latest_temperatures_list:
        dateString = str(t['date'].strftime('%Y-%m-%d %H:%M:%S'))
        del t['id']
        del t['date']
        del t['c0']
        for key in t.keys():
            for sensor in sensors:
                if(sensor['name'] == key):
                    sensor['values'].append({'date': dateString, 'temperature': t[key]})

    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")