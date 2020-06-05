from rest_framework import serializers
from .models import Client, Event


class FamilyPlanningRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class EventsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'
