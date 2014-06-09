from django.shortcuts import render


def index(request):
    return render(request, 'graphs/index.html')


def watchers(request):
    return render(request, 'graphs/watchers.html')


def rooms(request):
    return render(request, 'graphs/rooms.html')


def configureRooms(request):
    return render(request, 'graphs/configure-rooms.html')


def configureWatchers(request):
    return render(request, 'graphs/configure-watchers.html')