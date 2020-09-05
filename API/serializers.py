from rest_framework import serializers
from .models import Client, Event, ClientExtended, ReferralTask, Referral, Household, Clients


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class ClientExtendedSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientExtended
        fields = '__all__'


class EventsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class DashboardSummarySerializer(serializers.Serializer):

    total_services = serializers.IntegerField()
    total_clients = serializers.IntegerField()
    total_family_planning_registrations = serializers.IntegerField()
    total_family_planning_initiations = serializers.IntegerField()
    total_family_planning_discontinuations = serializers.IntegerField()


class ReferralTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReferralTask
        fields = '__all__'


class ReferralSerializer(serializers.ModelSerializer):

    class Meta:
        model =  Referral
        fields = '__all__'


class HouseholdSerializer(serializers.ModelSerializer):

    class Meta:
        model = Household
        fields = '__all__'


class ClientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clients
        fields = '__all__'
