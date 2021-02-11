import django_tables2 as tables
from Core import models as core_models



class TeamTable(tables.Table):
    class Meta:
        model = core_models.Team
        template_name = "django_tables2/bootstrap.html"
        fields = ("team_id","name","identifier", "uuid" )



class LocationTable(tables.Table):
    class Meta:
        model = core_models.Location
        template_name = "django_tables2/bootstrap.html"
        fields = ("location_id","name","description","uuid" )