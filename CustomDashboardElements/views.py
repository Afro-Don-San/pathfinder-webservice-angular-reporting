from django.shortcuts import render
from django.http import HttpResponse


def HandleFilters(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        location_uuid = request.POST["UUID"]

        print(date_from)
        print(date_to)
        print(location_uuid)

        return HttpResponse("worked")