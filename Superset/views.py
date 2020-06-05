from django.shortcuts import render
from django.http import HttpResponse
import webbrowser
# Create your views here.


def get_superset(request):
    if request.method == "GET":
        webbrowser.open("http://45.56.117.65/")
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=404)
