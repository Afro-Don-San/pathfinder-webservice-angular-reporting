import django_tables2 as tables
from Core import models as core_models
from django.utils.safestring import mark_safe
from django.utils.html import escape


class TeamActions(tables.Column):
    empty_values = list()

    def render(self, value, record):
        return mark_safe('<button id="%s" class="btn_add btn btn-primary'
                         ' btn-xs"><i class="la la-plus"></i>New Member</button> '
                         '<button id="%s" class="btn_update btn btn-info'
                         'btn-xs"><i class="la la-pencil"></i></button><button id="%s" class="btn_view btn btn-info'
                         'btn-xs"><i class="la la-list"></i></button>  '% (escape(record.id),escape(record.id), escape(record.id)))


class LocationActions(tables.Column):
    empty_values = list()

    def render(self, value, record):
        return mark_safe('<button id="%s" class="btn_add btn btn-primary'
                         ' btn-xs"><i class="la la-plus"></i>New Location</button> '
                         '<button id="%s" class="btn_update btn btn-info'
                         'btn-xs"><i class="la la-pencil"></i></button><button id="%s" class="btn_view btn btn-info'
                         'btn-xs"><i class="la la-list"></i></button>  '% (escape(record.id),escape(record.id), escape(record.id)))


class TeamTable(tables.Table):
    Actions = TeamActions()
    class Meta:
        model = core_models.Team
        template_name = "django_tables2/bootstrap.html"
        fields = ("team_id","name","identifier", "uuid" )
        row_attrs = {
            'data-id': lambda record: record.pk
        }


class LocationTable(tables.Table):
    Actions = LocationActions()
    class Meta:
        model = core_models.Location
        template_name = "django_tables2/bootstrap.html"
        fields = ("location_id","name","description","uuid" )


class ClientsTable(tables.Table):
    class Meta:
        model = core_models.Clients
        template_name = "django_tables2/bootstrap.html"
        fields = ("first_name","middle_name","last_name","gender", "phone_number", "birth_date" )


# class CHWTable(tables.Table):
#     chw_name = tables.Column()
#     chw_id = tables.Column()
#     value = tables.Column()
#
#     class Meta:
#         template_name = "django_tables2/bootstrap.html"
#         fields = ("chw_name", "chw_id", "value")
#
#
# class CHWReferralsTable(tables.Table):
#     chw_name = tables.Column()
#     chw_id = tables.Column()
#     issued = tables.Column()
#     completed = tables.Column()
#
#     class Meta:
#         template_name = "django_tables2/bootstrap.html"
#         fields = ("chw_name", "chw_id", "issued", "completed")
