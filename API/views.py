from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count
from django.conf import settings
from .serializers import EventsSerializer, FamilyPlanningRegistrationSerializer
from .models import Event, Client
import json
from rest_framework.decorators import action
import requests


def check_permission():
    headers = {"Authorization": "Basic Y2h3dHdvOlBhdGhmaW5kZXIxMjM=", "content-type": "application/json"}
    r = requests.get("http://172.105.87.198:8082/opensrp/security/authenticate/", headers=headers)
    return r.status_code


class FPRegistrationSummaryView(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = FamilyPlanningRegistrationSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Client.objects.all()
        serializer = FamilyPlanningRegistrationSerializer(queryset, many=True)
        total_aggregate = Client.objects.values('gender').annotate(value=Count('gender'))
        content = {'total_family_planning_registrations': queryset.count(),'total_aggregate':total_aggregate, 'records': serializer.data}
        return Response(content)

''
class EventsSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning')
        total_family_planning_discontinuation = Event.objects.filter(event_type='Family Planning Discontinuation')
        total_family_planning_registrations_by_team = Event.objects.filter(event_type='Family Planning Registration').\
            values('team').annotate(value=Count('team'))
        total_issued_services_by_team = Event.objects.all(). \
            values('team').annotate(value=Count('team'))
        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.values('event_type').annotate(value=Count('event_type'))
        content = {'total_events': queryset.count(),
                   'total_family_planning_initiations':total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuation.count(),
                   'total_services_aggregate': total_services_aggregate,
                   'total_family_planning_registrations_by_team':     total_family_planning_registrations_by_team,
                   'total_issued_services_by_team': total_issued_services_by_team,
                   'records': serializer.data}
        return Response(content)

