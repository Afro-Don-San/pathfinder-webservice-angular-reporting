from rest_framework import viewsets, status, generics
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.conf import settings
from .serializers import ClientSerializer, ClientChartSerializer
from .models import Client
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

