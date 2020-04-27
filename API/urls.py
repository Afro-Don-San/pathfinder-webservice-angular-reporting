from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('client_summary', views.ClientSummaryView)
router.register('event_summary', views.EventSummaryView)

urlpatterns = [
    path('', include(router.urls)),
]
