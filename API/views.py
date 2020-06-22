from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count, Sum
from django.conf import settings
from .serializers import EventsSerializer, ClientExtendedSerializer, DashboardSummarySerializer
from .models import Event, Client, ClientExtended
import json
from rest_framework.decorators import action
import requests
from datetime import datetime
from django.db import models
from django.db.models import Func
from django.db.models.functions import TruncMonth, ExtractMonth
import calendar


def check_permission():
    headers = {"Authorization": "Basic Y2h3dHdvOlBhdGhmaW5kZXIxMjM=", "content-type": "application/json"}
    r = requests.get("http://172.105.87.198:8082/opensrp/security/authenticate/", headers=headers)
    return r.status_code


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


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

        queryset = ClientExtended.objects.all()
        serializer = ClientExtendedSerializer(queryset, many=True)
        total_aggregate = ClientExtended.objects.all()\
            .values('gender').annotate(value=Count('gender'))
        content = {'total_aggregate': total_aggregate,
                   'records': serializer.data}
        return Response(content)


class EventsSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        query_service_providers = Event.objects.values('team_id', 'team').distinct()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration')
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning')
        total_family_planning_discontinuation = Event.objects.filter(event_type='Family Planning Discontinuation')
        total_family_planning_registrations_by_team = Event.objects.filter(event_type='Family Planning Registration').\
            values('team_id', 'team').annotate(value=Count('team_id'))
        total_issued_services_by_team = Event.objects.all(). \
            values('team_id', 'team').annotate(value=Count('team_id'))
        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.values('event_type').annotate(value=Count('event_type'))
        total_services_by_month = Event.objects.all().annotate(
            month_number=ExtractMonth('date_created')).values('month_number').annotate(
            value=Count('id')
        )

        converted_total_services_by_month = []

        for x in total_services_by_month:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_total_services_by_month.append({ 'month_name': month_name, 'value': month_value })

        content = {'total_events': queryset.count(),
                   'query_service_providers': query_service_providers,
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_initiations':total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuation.count(),
                   'total_services_aggregate': total_services_aggregate,
                   'total_family_planning_registrations_by_team':     total_family_planning_registrations_by_team,
                   'total_issued_services_by_team': total_issued_services_by_team,
                   'total_services_by_month':converted_total_services_by_month,
                   'records': serializer.data}
        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = request.data["facilities"]

        for x in facilities:
            print(x)

        queryset = Event.objects.filter(event_date__gte=from_date,
                                        event_date__lte=to_date, location_id__in=facilities)
        query_service_providers = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date, location_id__in=facilities).values('team').distinct()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration',
                                                                   event_date__gte=from_date,
                                                                   event_date__lte=to_date, location_id__in=facilities)
        total_family_planning_referrals = Event.objects.filter(event_type='Family Planning Referral',
                                                               event_date__gte=from_date,
                                                               event_date__lte=to_date, location_id__in=facilities)
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning',
                                                                 event_date__gte=from_date,
                                                                 event_date__lte=to_date,
                                                                 location_id__in=facilities)
        total_family_planning_discontinuations = Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                      event_date__gte=from_date,
                                                                      event_date__lte=to_date,
                                                                      location_id__in=facilities)
        total_family_planning_registrations_by_team = Event.objects.filter(event_type='Family Planning Registration',
                                                                           event_date__gte=from_date,
                                                                           event_date__lte=to_date,
                                                                           location_id__in=facilities
                                                                           ). \
            values('team_id').annotate(value=Count('team_id'))
        total_issued_services_by_team = Event.objects.filter(event_date__gte=from_date,
                                                             event_date__lte=to_date, location_id__in=facilities).\
                                                                values('team').annotate(value=Count('team_id'))
        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.filter(event_date__gte=from_date,
                                                        event_date__lte=to_date, location_id__in=facilities).\
                                                            values('event_type').annotate(value=Count('event_type'))
        total_services_by_month = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date, location_id__in=facilities
                                                       ).annotate(
            month_number=ExtractMonth('date_created'),
        ).values('month_number').annotate(
            value=Count('id')
        )

        converted_total_services_by_month = []

        for x in total_services_by_month:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_total_services_by_month.append({'month_name': month_name, 'value': month_value})

        content = {'total_events': queryset.count(),
                   'query_service_providers': query_service_providers,
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_referrals': total_family_planning_referrals.count(),
                   'total_family_planning_initiations': total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuations.count(),
                   'total_services_aggregate': total_services_aggregate,
                   'total_family_planning_registrations_by_team': total_family_planning_registrations_by_team,
                   'total_issued_services_by_team': total_issued_services_by_team,
                   'total_services_by_month': converted_total_services_by_month,
                   'records': serializer.data}
        return Response(content)


class DashboardSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = DashboardSummarySerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        total_clients = Client.objects.all()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration')
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning')
        total_family_planning_discontinuation = Event.objects.filter(event_type='Family Planning Discontinuation')
        content = {'total_services': queryset.count(),
                   'total_clients': total_clients.count(),
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_initiations':total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuation.count()
                  }
        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        facilities = request.data["facilities"]

        queryset = Event.objects.filter(location_id__in=facilities)
        total_clients = Client.objects.all()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration',
                                                                   location_id__in=facilities)
        total_family_planning_referrals = Event.objects.filter(event_type='Family Planning Referral',
                                                               location_id__in=facilities)
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning',
                                                                 location_id__in=facilities)
        total_family_planning_discontinuations = Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                      location_id__in=facilities)

        content = {'total_services': queryset.count(),
                   'total_clients': total_clients.count(),
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_referrals': total_family_planning_referrals.count(),
                   'total_family_planning_initiations': total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuations.count()}
        return Response(content)


