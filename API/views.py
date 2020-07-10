from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count, Sum
from django.conf import settings
from .serializers import EventsSerializer, ClientExtendedSerializer, DashboardSummarySerializer
from .models import Event, Client, ClientExtended, EventExtended
import json
from rest_framework.decorators import action
import requests
from datetime import datetime
from django.db import models
from django.db.models import Func, Q
from django.db.models.functions import TruncMonth, ExtractMonth
import calendar


def check_permission():
    headers = {"Authorization": "Basic Y2h3dHdvOlBhdGhmaW5kZXIxMjM=", "content-type": "application/json"}
    r = requests.get("http://172.105.87.198:8082/opensrp/security/authenticate/", headers=headers)
    return r.status_code


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


class ClientsSummaryView(viewsets.ModelViewSet):
    queryset = ClientExtended.objects.select_related()
    serializer_class = ClientExtendedSerializer
    permission_classes = ()

    def list(self, request):
        queryset = ClientExtended.objects.all()
        serializer = ClientExtendedSerializer(queryset, many=True)
        total_aggregate = ClientExtended.objects.select_related().values('gender').annotate(value=Count('gender'))
        content = {'total_family_planning_registrations': queryset.count(),'total_aggregate':total_aggregate, 'records': serializer.data}
        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = request.data["facilities"]

        queryset = ClientExtended.objects.all()
        serializer = ClientExtendedSerializer(queryset, many=True)
        total_aggregate = ClientExtended.objects.all()\
            .values('gender').annotate(value=Count('gender'))
        content = {'total_aggregate': total_aggregate,
                   'records': serializer.data}
        return Response(content)


class EventsSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        query_service_providers = Event.objects.values('team_id', 'team').distinct()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration')
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning')
        total_family_planning_discontinuation = Event.objects.filter(event_type='Family Planning Discontinuation')
        total_family_planning_registrations_by_team = Event.objects.filter(event_type='Family Planning Registration').\
            values('team_id', 'team').annotate(value=Count('team_id'))
        total_issued_services_by_team = Event.objects.all(). \
            values('team_id', 'team').annotate(value=Count('team_id'))
        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.values('event_type').annotate(value=Count('event_type'))
        total_services_by_month = Event.objects.all().annotate(
            month_number=ExtractMonth('date_created')).values('month_number').annotate(
            value=Count('id')
        )

        total_family_planning_method_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                                          values_1='true'). \
            values('field_code_3').annotate(value=Count('field_code_3'))

        total_issued_referrals = Event.objects.all(). \
            filter(Q(event_type='Referrals') | Q(event_type='ANC Referrals') | Q(event_type='Family Planning Referral')
                   | Q(event_type='Family Planning Referral Followup')).values('event_type'). \
            annotate(value=Count('event_type'))

        family_planning_method_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                                values_2="true").values('field_code_3').\
            annotate(value=Count('values_4'))

        converted_total_services_by_month = []

        for x in total_services_by_month:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_total_services_by_month.append({ 'month_name': month_name, 'value': month_value })

        content = {'total_events': queryset.count(),
                   'query_service_providers': query_service_providers,
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_initiations':total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuation.count(),
                   'total_services_aggregate': total_services_aggregate,
                   'total_family_planning_registrations_by_team':     total_family_planning_registrations_by_team,
                   'total_issued_services_by_team': total_issued_services_by_team,
                   'total_services_by_month':converted_total_services_by_month,
                   'total_family_planning_method_given': total_family_planning_method_given,
                   'total_issued_referrals':total_issued_referrals,
                   'family_planning_method_given': family_planning_method_given,
                   'records': serializer.data}
        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = list(request.data["facilities"])

        queryset = Event.objects.filter(event_date__gte=from_date,
                                        event_date__lte=to_date, location_id__in=facilities)
        query_service_providers = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date, location_id__in=facilities).values('team').distinct()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration',
                                                                   event_date__gte=from_date,
                                                                   event_date__lte=to_date, location_id__in=facilities)
        total_family_planning_referrals = Event.objects.filter(event_type='Family Planning Referral',
                                                               event_date__gte=from_date,
                                                               event_date__lte=to_date, location_id__in=facilities)
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning',
                                                                 event_date__gte=from_date,
                                                                 event_date__lte=to_date,
                                                                 location_id__in=facilities)
        total_family_planning_discontinuations = Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                      event_date__gte=from_date,
                                                                      event_date__lte=to_date,
                                                                      location_id__in=facilities)
        total_family_planning_registrations_by_team = Event.objects.filter(event_type='Family Planning Registration',
                                                                           event_date__gte=from_date,
                                                                           event_date__lte=to_date,
                                                                           location_id__in=facilities
                                                                           ). \
            values('team_id').annotate(value=Count('team_id'))
        total_issued_referrals = Event.objects.filter(event_date__gte=from_date,
                                                      event_date__lte=to_date, location_id__in=facilities).\
            filter(Q(event_type='ANC Referral') | Q(event_type='Family Planning Referral')
                     | Q(event_type='Family Planning Referral Followup')).values('event_type').\
                        annotate(value=Count('event_type'))

        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.filter(event_date__gte=from_date,
                                                        event_date__lte=to_date, location_id__in=facilities).\
                                                            values('event_type').annotate(value=Count('event_type'))
        total_services_by_month = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date, location_id__in=facilities
                                                       ).annotate(
            month_number=ExtractMonth('date_created'),
        ).values('month_number').annotate(
            value=Count('id')
        )

        total_family_planning_method_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                                          values_2="true",
                                                                          event_date__gte=from_date,
                                                                          event_date__lte=to_date, location_id__in=facilities
                                                                          ).\
            values('field_code_3').annotate(value=Count('field_code_3'))

        family_planning_method_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                                          values_2="true",
                                                                          event_date__gte=from_date,
                                                                          event_date__lte=to_date, location_id__in=facilities
                                                                          ). \
            values('field_code_3').annotate(value=Count('values_4'))

        converted_total_services_by_month = []

        for x in total_services_by_month:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_total_services_by_month.append({'month_name': month_name, 'value': month_value})

        content = {'total_events': queryset.count(),
                   'query_service_providers': query_service_providers,
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_referrals': total_family_planning_referrals.count(),
                   'total_family_planning_initiations': total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuations.count(),
                   'total_services_aggregate': total_services_aggregate,
                   'total_family_planning_registrations_by_team': total_family_planning_registrations_by_team,
                   'total_issued_referrals': total_issued_referrals,
                   'total_services_by_month': converted_total_services_by_month,
                   'total_family_planning_method_given':total_family_planning_method_given,
                   'family_planning_method_given': family_planning_method_given,
                   'records': serializer.data}
        return Response(content)


class DashboardSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = DashboardSummarySerializer
    permission_classes = ()

    def list(self, request):
        queryset = Event.objects.all()
        total_clients = Client.objects.all()
        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration')
        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning')
        total_family_planning_discontinuation = Event.objects.filter(event_type='Family Planning Discontinuation')
        total_clients_families = Client.objects.filter(unique_id__contains='family')
        content = {'total_services': queryset.count(),
                   'total_clients': total_clients.count(),
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_family_planning_initiations':total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuation.count(),
                   'total_clients_families':total_clients_families.count()
                  }
        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        facilities = request.data["facilities"]

        queryset = Event.objects.filter(location_id__in=facilities)

        list_families = []

        total_clients_families = Client.objects.filter(unique_id__contains='family')

        for x in total_clients_families:
            list_families.append(int(x.id))

        total_clients = Client.objects.exclude(id__in=list_families)

        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration',
                                                                   location_id__in=facilities)
        total_referrals = Event.objects.filter\
            (Q(event_type='Family Planning Referral') |
             Q(event_type='ANC Referral')).filter(location_id__in = facilities)

        total_family_planning_initiations = Event.objects.filter(event_type='Introduction to Family Planning',
                                                                 location_id__in=facilities)
        total_family_planning_discontinuations = Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                      location_id__in=facilities)

        content = {'total_services': queryset.count(),
                   'total_clients': total_clients.count(),
                   'total_family_planning_registrations': total_family_planning_registrations.count(),
                   'total_referrals': total_referrals.count(),
                   'total_family_planning_initiations': total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuations.count(),
                   'total_clients_families':total_clients_families.count()}
        return Response(content)


class CitizenReportCardView(viewsets.ModelViewSet):
    queryset = EventExtended.objects.filter(event_type="Citizen Report Card")
    serializer_class=  EventsSerializer
    permission_classes = ()

    def list(self, request):
        willing_to_participate_in_survey = EventExtended.objects.filter\
            (event_type='Citizen Report Card').\
            values('values_1').\
            annotate(value=Count('values_1'))

        name_of_health_facility_visited_for_family_planning_services = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_2'). \
            annotate(value=Count('values_2'))

        residence = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_3'). \
            annotate(value=Count('values_3'))

        education = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_4'). \
            annotate(value=Count('values_4'))

        occupation = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_5'). \
            annotate(value=Count('values_5'))

        marital_status = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_6'). \
            annotate(value=Count('values_6'))

        religion = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_7'). \
            annotate(value=Count('values_7'))

        reasons_for_people_not_going_to_health_facilities = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_8'). \
            annotate(value=Count('values_8'))

        means_of_transport_to_facility = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_9'). \
            annotate(value=Count('values_9'))

        time_to_reach_closest_facility = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_10'). \
            annotate(value=Count('values_10'))

        is_this_the_nearest_facility_from_home = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_11'). \
            annotate(value=Count('values_11'))

        was_the_facility_open_when_you_arrived = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_12'). \
            annotate(value=Count('values_12'))

        did_you_get_family_planning_information_at_the_reception = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_13'). \
            annotate(value=Count('values_13'))

        how_long_it_took_to_be_attended_by_service_provider = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_14'). \
            annotate(value=Count('values_14'))

        did_the_service_provider_make_you_feel_welcome = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_15'). \
            annotate(value=Count('values_15'))

        did_the_service_provider_assure_confidentiality = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_16'). \
            annotate(value=Count('values_16'))

        did_you_meet_the_service_providers_in_a_private_room = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_17'). \
            annotate(value=Count('values_17'))

        did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_18'). \
            annotate(value=Count('values_18'))

        did_the_service_providers_use_visual_aids_to_demo_fp_methods = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_19'). \
            annotate(value=Count('values_19'))

        did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_20'). \
            annotate(value=Count('values_20'))

        were_you_given_info_on_dual_protection = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_21'). \
            annotate(value=Count('values_21'))

        methods_not_wanted = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_22'). \
            annotate(value=Count('values_22'))

        citizen_card_records = EventExtended.objects.filter(event_type='Citizen Report Card')

        converted_citizen_card_report = []

        for x in citizen_card_records:
            print(x)
            # willing_to_participate_in_survey = x['values_1']
            # name_of_health_facility_visited_for_family_planning_services = x['values_2']
            # residence = x['values_3']
            # education = x['values_4']
            # occupation = x['values_5']
            # marital_status = x['values_6']
            # religion = x['values_7']
            # reasons_for_people_not_going_to_health_facilities = x['values_8']
            # means_of_transport_to_facility = x['values_9']
            # time_to_reach_closest_facility = x['values_10']
            # is_this_the_nearest_facility_from_home = x['values_11']
            # was_the_facility_open_when_you_arrived = x['values_12']
            # did_you_get_family_planning_information_at_the_reception = x['values_13']
            # how_long_it_took_to_be_attended_by_service_provider = x['values_14']
            # did_the_service_provider_make_you_feel_welcome = x['values_15']
            # did_the_service_provider_assure_confidentiality = x['values_16']
            # did_you_meet_the_service_providers_in_a_private_room = x['values_17']
            # did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods = x['values_18']
            # did_the_service_providers_use_visual_aids_to_demo_fp_methods = x['values_19']
            # did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods = x['values_20']
            # were_you_given_info_on_dual_protection = x['values_21']
            # methods_not_wanted = x['values_22']

            # converted_citizen_card_report.append({'willing_to_participate_in_survey': willing_to_participate_in_survey,
            #                                       'name_of_health_facility_visited_for_family_planning_services':
            #                                           name_of_health_facility_visited_for_family_planning_services,
            #                                       'residence': residence,
            #                                       'education': education,
            #                                       'occupation': occupation,
            #                                       'marital_status': marital_status,
            #                                       'religion': religion,
            #                                       'reasons_for_people_not_going_to_health_facilities':
            #                                           reasons_for_people_not_going_to_health_facilities,
            #                                       'means_of_transport_to_facility': means_of_transport_to_facility})

        content = {'records':converted_citizen_card_report,'willing_to_participate_in_survey':
                                willing_to_participate_in_survey,
                   'name_of_health_facility_visited_for_family_planning_services':
                       name_of_health_facility_visited_for_family_planning_services,
                   'residence': residence,
                   'education': education,
                   'occupation':occupation,
                   'marital_status': marital_status,
                   'religion': religion,
                   'reasons_for_people_not_going_to_health_facilities': reasons_for_people_not_going_to_health_facilities,
                   'means_of_transport_to_facility': means_of_transport_to_facility,
                   'time_to_reach_closest_facility': time_to_reach_closest_facility,
                   'is_this_the_nearest_facility_from_home' : is_this_the_nearest_facility_from_home,
                   'was_the_facility_open_when_you_arrived': was_the_facility_open_when_you_arrived,
                   'did_you_get_family_planning_information_at_the_reception': did_you_get_family_planning_information_at_the_reception,
                   'how_long_it_took_to_be_attended_by_service_provider': how_long_it_took_to_be_attended_by_service_provider,
                   'did_the_service_provider_make_you_feel_welcome': did_the_service_provider_make_you_feel_welcome,
                   'did_the_service_provider_assure_confidentiality': did_the_service_provider_assure_confidentiality,
                   'did_you_meet_the_service_providers_in_a_private_room':
                       did_you_meet_the_service_providers_in_a_private_room,
                   'did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods':
                       did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods,
                   'did_the_service_providers_use_visual_aids_to_demo_fp_methods':
                       did_the_service_providers_use_visual_aids_to_demo_fp_methods,
                   'did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods':
                       did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods,
                   'were_you_given_info_on_dual_protection': were_you_given_info_on_dual_protection,
                   'methods_not_wanted': methods_not_wanted

                   }

        return Response(content)


class FamilyPlanningMethodView(viewsets.ModelViewSet):
    queryset = EventExtended.objects.filter(event_type="Give Family Planning Method")
    serializer_class=  EventsSerializer
    permission_classes = ()

    def list(self):
        family_planning_method_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                                    values_2="true").values('field_code_3'). \
            annotate(value=Count('values_4'))

        total_family_planning_method_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                                    values_2="true").values('field_code_3'). \
            annotate(value=Count('values_4'))









