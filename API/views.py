from rest_framework import viewsets, status, generics
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.conf import settings
from .serializers import ClientSerializer
from .models import Client
import json
from rest_framework.decorators import action


class ClientView(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Client.objects.all()

        serializer = ClientSerializer(queryset, many=True)
        content =  {'total_clients': queryset.count(), 'records': serializer.data}
        return Response(content)
