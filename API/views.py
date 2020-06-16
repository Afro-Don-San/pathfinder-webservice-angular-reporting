from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count
from django.conf import settings
from .serializers import EventsSerializer, ClientExtendedSerializer
from .models import Event, Client, ClientExtended
import json
from rest_framework.decorators import action
import requests
from datetime import datetime


def check_permission():
    headers = {"Authorization": "Basic Y2h3dHdvOlBhdGhmaW5kZXIxMjM=", "content-type": "application/json"}
    r = requests.get("http://172.105.87.198:8082/opensrp/security/authenticate/", headers=headers)
    return r.status_code


class ClientsSummaryView(viewsets.ModelViewSet):
    queryset = ClientExtended.objects.select_related()
    serializer_class = ClientExtendedSerializer
    permission_classes = ()

    def list(self, request):
        queryset = ClientExtended.objects.all()
        serializer = ClientExtendedSerializer(queryset, many=True)
        total_aggregate = ClientExtended.objects.select_related().values('gender').annotate(value=Count('gender'))
        content = {'total_family_planning_registrations': queryset.count(),'total_aggregate':total_aggregate, 'records': serializer.data}
        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = request.data["facilities"]

        queryset = ClientExtended.objects.filter(date_time_created__gte=from_date, date_time_created__lte=to_date)
        serializer = ClientExtendedSerializer(queryset, many=True)
        total_aggregate = ClientExtended.objects.filter(date_time_created__gte=from_date, date_time_created__lte=to_date).all()\
            .values('gender').annotate(value=Count('gender'))
        content = {'total_family_planning_registrations': queryset.count(), 'total_aggregate': total_aggregate,
                   'records': serializer.data}
        return Response(content)


class EventsSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        query_service_providers = Event.objects.values('team').distinct()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration')
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning')
        total_family_planning_discontinuation = Event.objects.filter(event_type='Family Planning Discontinuation')
        total_family_planning_registrations_by_team = Event.objects.filter(event_type='Family Planning Registration').\
            values('team').annotate(value=Count('team'))
        total_issued_services_by_team = Event.objects.all(). \
            values('team').annotate(value=Count('team'))
        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.values('event_type').annotate(value=Count('event_type'))
        content = {'total_events': queryset.count(),
                   'query_service_providers': query_service_providers,
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_initiations':total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuation.count(),
                   'total_services_aggregate': total_services_aggregate,
                   'total_family_planning_registrations_by_team':     total_family_planning_registrations_by_team,
                   'total_issued_services_by_team': total_issued_services_by_team,
                   'records': serializer.data}
        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = request.data["facilities"]

        queryset = Event.objects.filter(event_date__gte=from_date,
                                        event_date__lte=to_date)
        query_service_providers = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date).values('team').distinct()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration',
                                                                   event_date__gte=from_date,
                                                                   event_date__lte=to_date)
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning',
                                                                 event_date__gte=from_date,
                                                                 event_date__lte=to_date)
        total_family_planning_discontinuations = Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                      event_date__gte=from_date,
                                                                      event_date__lte=to_date)
        total_family_planning_registrations_by_team = Event.objects.filter(event_type='Family Planning Registration',
                                                                           event_date__gte=from_date,
                                                                           event_date__lte=to_date
                                                                           ). \
            values('team').annotate(value=Count('team'))
        total_issued_services_by_team = Event.objects.filter(event_date__gte=from_date,
                                                             event_date__lte=to_date).\
                                                                values('team').annotate(value=Count('team'))
        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.filter(event_date__gte=from_date,
                                                        event_date__lte=to_date).\
                                                            values('event_type').annotate(value=Count('event_type'))
        content = {'total_events': queryset.count(),
                   'query_service_providers': query_service_providers,
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_initiations': total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuations.count(),
                   'total_services_aggregate': total_services_aggregate,
                   'total_family_planning_registrations_by_team': total_family_planning_registrations_by_team,
                   'total_issued_services_by_team': total_issued_services_by_team,
                   'records': serializer.data}
        return Response(content)


