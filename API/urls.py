from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('clients_summary', views.ClientsSummaryView, basename="clients_summary")
router.register('events_summary', views.EventsSummaryView, basename="events_summary")
router.register('dashboard_summary', views.DashboardSummaryView, basename="dashboard_summary")
router.register('citizen_report_card', views.CitizenReportCardView, basename='citizen_report_card')
router.register('family_planning_methods_given', views.FamilyPlanningMethodView,
                basename='family_planning_methods_given')
router.register('map_summary', views.MapSummaryView, basename='map_summary')
router.register('referral_summary', views.ReferralTaskView, basename='referral_types_focus')
router.register('clients_families', views.ClientsView, basename='clients')

urlpatterns = [
    path('', include(router.urls)),
]
