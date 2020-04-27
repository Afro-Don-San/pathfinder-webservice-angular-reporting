from rest_framework import serializers
from .models import Client, Event


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ('__all__')


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'

