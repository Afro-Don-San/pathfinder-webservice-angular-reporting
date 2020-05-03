from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count
from django.conf import settings
from .serializers import ClientSerializer, EventSerializer
from .models import Client, Event
import json
from rest_framework.decorators import action
import requests


def check_permission():
    headers = {"Authorization": "Basic Y2h3dHdvOlBhdGhmaW5kZXIxMjM=", "content-type": "application/json"}
    r = requests.get("http://172.105.87.198:8082/opensrp/security/authenticate/", headers=headers)
    return r.status_code


class ClientSummaryView(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (AllowAny,)

    def list(self, request):
        if check_permission() == 200:
            queryset = Client.objects.all()
            serializer = ClientSerializer(queryset, many=True)
            total_aggregate = Client.objects.values('gender').annotate(value=Count('gender'))
            content = {'total': queryset.count(),'total_aggregate':total_aggregate, 'records': serializer.data}
        else:
            content = {"Authorization failed."}
        return Response(content)


class EventSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        queryset_referral = Event.objects.filter(event_type='Referral')
        total_family_planning_registration_by_team = Event.objects.filter(event_type='Family Planning Registration').\
            values('team').annotate(value=Count('team'))
        total_issued_referrals_by_team = Event.objects.filter(event_type='Referral'). \
            values('team').annotate(value=Count('team'))
        serializer = EventSerializer(queryset, many=True)
        total_aggregate = Event.objects.values('event_type').annotate(value=Count('event_type'))
        content = {'total': queryset.count(), 'total_referral':queryset_referral.count(),
                   'total_aggregate': total_aggregate,
                   'total_family_planning_registration_by_team': total_family_planning_registration_by_team,
                   'total_issued_referrals_by_team': total_issued_referrals_by_team,
                   'records': serializer.data}
        return Response(content)

