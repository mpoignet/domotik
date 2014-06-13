from collections import OrderedDict
import json
import csv
import datetime
import calendar

from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, Template
from django.http import HttpResponse
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

import pytz

from backend.models import Sensor, Record, Room
from backend.serializers import RoomSerializer

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def create_record(request):
    date = request.POST.get('date')
    measure = request.POST.get('measure')
    sensor_address = request.POST.get('address')

    sensors = Sensor.objects.filter(address=sensor_address)
    if not sensors:
        sensor = Sensor(address=sensor_address)
        sensor.save()
    else:
        sensor = sensors[0]

    record = Record(date=date, measure=measure, sensor_id=sensor.id)
    record.save()
    return HttpResponse(json.dumps(model_to_dict(record)), content_type="application/json")


def get_sensor_list(request):
    sensor_list = Sensor.objects.all().values()
    sensors = []
    for sensor in sensor_list:
        s = {}
        if not sensor['name']:
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']
        s['id'] = sensor['id']
        sensors.append(s)
    return HttpResponse(json.dumps({'sensors': sensors}), content_type="application/json")


def get_records(request):
    sensor_list = request.GET.getlist('sensors', [])
    if sensor_list:
        sensor_list = Sensor.objects.filter(pk__in=sensor_list).values()
    else:
        sensor_list = Sensor.objects.all().values()
    start_date = request.GET.get('startDate', '')
    end_date = request.GET.get('endDate', '')

    output = request.GET.get('output', 'json')
    if output == 'csv':
        return return_csv(sensor_list, start_date, end_date)
    if output == 'flot':
        return return_flot(sensor_list, start_date, end_date)
    if output == 'morris':
        return return_morris(sensor_list, start_date, end_date)
    return return_json(sensor_list, start_date, end_date)


def get_records_for_sensor(sensor_id, start_date, end_date):
    if start_date:
        start_date = datetime.datetime.fromtimestamp(
            int(start_date), pytz.timezone('CET')).strftime('%Y-%m-%d %H:%M:%S')
    if end_date:
        end_date = datetime.datetime.fromtimestamp(int(end_date), pytz.timezone(
            'CET')).strftime('%Y-%m-%d %H:%M:%S')
    if start_date and end_date:
        print "DATES"
        print start_date
        print end_date
        records = Record.objects.filter(sensor_id=sensor_id).filter(
            date__gte=start_date).filter(date__lte=end_date)
        print sensor_id
        print records
    elif start_date:
        records = Record.objects.filter(sensor_id=sensor_id).filter(
            date__gte=start_date)
    else:
        records = Record.objects.filter(sensor_id=sensor_id).order_by('-date')[0:250]
    return records


def return_morris(sensor_list, start_date, end_date):
    sensors = []
    dates = {}
    for sensor in sensor_list:
        if not sensor['name']:
            sensor_name = str(sensor['address'])
        else:
            sensor_name = sensor['name']
        records = get_records_for_sensor(sensor['id'], start_date, end_date)
        if len(records) > 0:
            sensors.append(sensor_name)
            for record in records:
                date_string = str(record.date.strftime('%Y-%m-%d %H:%M:%S'))
                if not date_string in dates:
                    dates[date_string] = {}
                dates[date_string][sensor_name] = record.measure

    elements = []
    for date in dates:
        element = {'date': date}
        for sensor in dates[date]:
            element[sensor] = dates[date][sensor]
        elements.append(element)

    return HttpResponse(json.dumps({'mElements': elements}),
                        content_type="application/json")


def return_flot(sensor_list, start_date, end_date):
    sensors = []
    for sensor in sensor_list:
        s = {}
        if not sensor['name']:
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']
        s['values'] = []
        records = get_records_for_sensor(sensor['id'], start_date, end_date)
        if len(records) > 0:
            for record in records:
                # javascript timestamps are in ms, unix timestamp in s, hence the *1000
                timestamp = calendar.timegm(record.date.timetuple()) * 1000
                s['values'].append((timestamp, record.measure))
            sensors.append(s)

    return HttpResponse(json.dumps({'sensors': sensors}),
                        content_type="application/json")


def return_json(sensor_list, start_date, end_date):
    sensors = []
    for sensor in sensor_list:
        s = {}
        if not sensor['name']:
            s['name'] = str(sensor['address'])
        else:
            s['name'] = sensor['name']
        s['values'] = []
        records = get_records_for_sensor(sensor['id'], start_date, end_date)
        if len(records) > 0:
            for record in records:
                date_string = str(record.date.strftime('%Y-%m-%d %H:%M:%S'))
                s['values'].append(
                    {'date': date_string, 'temperature': record.measure})
            sensors.append(s)

    return HttpResponse(json.dumps({'sensors': sensors}),
                        content_type="application/json")


def return_csv(sensor_list, start_date, end_date):
    sensors = []
    dates = {}
    for sensor in sensor_list:
        if not sensor['name']:
            sensor_name = str(sensor['address'])
        else:
            sensor_name = sensor['name']
        records = get_records_for_sensor(sensor['id'], start_date, end_date)
        if len(records) > 0:
            sensors.append(sensor_name)
            for record in records:
                date_string = str(record.date.strftime('%Y-%m-%d %H:%M:%S'))
                if not date_string in dates:
                    dates[date_string] = {}
                dates[date_string][sensor_name] = record.measure

    header = ['date']
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


def get_rooms(request):
    if request.method == 'GET':
        # rooms = Room.objects.all()
        # serializer = RoomSerializer(rooms, many=True)
        # return JSONResponse(serializer.data)
        rooms = []
        for room in Room.objects.all():
            room_dict = model_to_dict(room)
            sensors = Sensor.objects.filter(room_id=room_dict['id'])
            if sensors:
                room_dict['sensor'] = model_to_dict(sensors[0])
                record = Record.objects.filter(sensor_id=sensors[0].id).order_by('-date')[0]
                room_dict['lastMeasure'] = {
                    'date': str(record.date.strftime('%Y-%m-%d %H:%M:%S')),
                    'measure': record.measure}
            rooms.append(room_dict)
        return HttpResponse(json.dumps({'rooms': rooms}), content_type="application/json")
    elif request.method == 'POST':
        room_name = request.POST.get('name')
        sensor_id = request.POST.get('id')
        room = Room(name=room_name, sensor_id=sensor_id)
        room.save()
        new_room = Room.objects.get(id=room.id)
        c = RequestContext(request,
                           {'room': json.dumps(model_to_dict(new_room))})
        t = Template(
            "{% autoescape off %}{{room}}{% endautoescape %} ")  # A dummy template
        response = HttpResponse(t.render(c), mimetype=u'application/json')
        return response


# @api_view(['GET', 'PATCH'])
# def update_room(request, room_id):
#     if not room_id:
#         return False
#     room = Room.objects.get(id=room_id)
#     if not room:
#         return False
#     if request.method == 'PATCH':
#         data = JSONParser().parse(request)
#         print data
#         actions = request.DATA.getlist('actions')
#         for action in actions:
#             if action.op == 'toggle' and action.field == 'isControlled':
#                 room = toggle_control(room)
#                 room.save()
#     return HttpResponse(json.dumps(model_to_dict(room)), content_type="application/json")


def toggle_control(request):
    room_id = request.POST.get('id')
    room = Room.objects.get(id=room_id)
    if room.isControlled:
        room.isControlled = False
    else:
        room.isControlled = True

    room.save()
    return HttpResponse(json.dumps(room.isControlled), content_type="application/json")


def add_to_temperature(request):
    room_id = request.POST.get('id')
    delta_t = request.POST.get('t')
    room = Room.objects.get(id=room_id)
    room.temperature += int(delta_t)
    room.save()
    return HttpResponse(json.dumps(room.temperature), content_type="application/json")

@csrf_exempt
def handle_records(request):
    if request.method == 'GET':
        return get_records(request)
    if request.method == 'POST':
        return create_record(request)