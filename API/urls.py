from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('clients_summary', views.ClientsSummaryView, basename="clients_summary")
router.register('events_summary', views.EventsSummaryView, basename="events_summary")
router.register('dashboard_summary', views.DashboardSummaryView, basename="dashboard_summary")

urlpatterns = [
    path('', include(router.urls)),
]
