from django.contrib import admin
from Core import models as core_models

# Register your models here.

class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_id', 'name', 'description', 'parent_location')
    search_fields = ['name']


admin.site.register(core_models.Location, LocationAdmin)