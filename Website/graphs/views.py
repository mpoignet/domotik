from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

# Create your views here.


def index(request):
    template = loader.get_template('graphs/index.html')
    return render(request, 'graphs/index.html')

def watchers(request):
    template = loader.get_template('graphs/watchers.html')
    return render(request, 'graphs/watchers.html')

def rooms(request):
    template = loader.get_template('graphs/rooms.html')
    return render(request, 'graphs/rooms.html')

def configureRooms(request):
    template = loader.get_template('graphs/configure-rooms.html')
    return render(request, 'graphs/configure-rooms.html')

def configureWatchers(request):
    template = loader.get_template('graphs/configure-watchers.html')
    return render(request, 'graphs/configure-watchers.html')