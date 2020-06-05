from django.urls import path, include
from . import views

urlpatterns = [
    path('analytics', views.get_superset, name= 'get_superset'),
]
