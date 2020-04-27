from rest_framework import viewsets, status, generics
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.conf import settings
from .serializers import ClientSerializer, EventSerializer
from .models import Client, Event
import json
from rest_framework.decorators import action


class ClientSummaryView(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Client.objects.all()
        serializer = ClientSerializer(queryset, many=True)
        total_aggregate = Client.objects.values('gender').annotate(value=Count('gender'))
        content = {'total': queryset.count(),'total_aggregate':total_aggregate, 'records': serializer.data}
        return Response(content)


class EventSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        serializer = EventSerializer(queryset, many=True)
        total_aggregate = Event.objects.values('event_type').annotate(value=Count('event_type'))
        content = {'total': queryset.count(), 'total_aggregate': total_aggregate, 'records': serializer.data}
        return Response(content)


