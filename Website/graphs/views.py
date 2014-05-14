from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from temperatures.models import Data

# Create your views here.


def index(request):
    template = loader.get_template('graphs/index.html')

    return render(request, 'graphs/index.html')