from django.contrib import admin
from django.urls import path, include
from Core import views as core_views

urlpatterns = [

    path('get_parent_child_relationship/',core_views.get_parent_child_relationship, name="get_parent_child_relationship" )
]
