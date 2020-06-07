from django.urls import path
from . import views


urlpatterns = [
    path('filters',views.HandleFilters, name='handle_filters'),
]
