from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('family_planning_registration_summary', views.ClientsSummaryView)
router.register('events_summary', views.EventsSummaryView)

urlpatterns = [
    path('', include(router.urls)),
]
