from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('family_planning_registration_summary', views.FPRegistrationSummaryView)
router.register('referral_summary', views.ReferralsSummaryView)

urlpatterns = [
    path('', include(router.urls)),
]
