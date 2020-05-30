from rest_framework import serializers
from .models import FamilyPlanningRegistration, Referral


class FamilyPlanningRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = FamilyPlanningRegistration
        fields = '__all__'


class ReferralSerializer(serializers.ModelSerializer):

    class Meta:
        model = Referral
        fields = '__all__'
