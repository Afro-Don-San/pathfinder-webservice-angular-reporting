from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count
from django.conf import settings
from .serializers import ReferralSerializer, FamilyPlanningRegistrationSerializer
from .models import Referral, FamilyPlanningRegistration
import json
from rest_framework.decorators import action
import requests


def check_permission():
    headers = {"Authorization": "Basic Y2h3dHdvOlBhdGhmaW5kZXIxMjM=", "content-type": "application/json"}
    r = requests.get("http://172.105.87.198:8082/opensrp/security/authenticate/", headers=headers)
    return r.status_code


class FPRegistrationSummaryView(viewsets.ModelViewSet):
    queryset = FamilyPlanningRegistration.objects.all()
    serializer_class = FamilyPlanningRegistrationSerializer
    permission_classes = ()

    def list(self, request):
        queryset = FamilyPlanningRegistration.objects.all()
        serializer = FamilyPlanningRegistrationSerializer(queryset, many=True)
        total_aggregate = FamilyPlanningRegistration.objects.values('gender').annotate(value=Count('gender'))
        content = {'total_family_planning_registrations': queryset.count(),'total_aggregate':total_aggregate, 'records': serializer.data}
        return Response(content)


class ReferralsSummaryView(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Referral.objects.all()
        total_family_planning_referrals_by_team = Referral.objects.filter(referral_type='Family Planning Referral').\
            values('team').annotate(value=Count('team'))
        total_issued_referrals_by_team = Referral.objects.all(). \
            values('team').annotate(value=Count('team'))
        serializer = ReferralSerializer(queryset, many=True)
        total_aggregate = Referral.objects.values('referral_type').annotate(value=Count('referral_type'))
        content = {'total_referrals': queryset.count(),
                   'total_aggregate': total_aggregate,
                   'total_family_planning_referral_by_team': total_family_planning_referrals_by_team,
                   'total_issued_referrals_by_team': total_issued_referrals_by_team,
                   'records': serializer.data}
        return Response(content)

