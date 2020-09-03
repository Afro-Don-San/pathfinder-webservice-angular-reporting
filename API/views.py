from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count, Sum
from django.conf import settings
from .serializers import EventsSerializer, ClientExtendedSerializer, DashboardSummarySerializer
from .models import Event, Client, ClientExtended, EventExtended, Clients, Household
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

        print(facilities)

        queryset = Event.objects.filter(event_date__gte=from_date,
                                        event_date__lte=to_date, location_id__in=facilities)
        query_service_providers = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date, location_id__in=facilities).values('team').distinct()
        total_anc_referrals = Event.objects.filter(event_type='ANC Referral',
                                                                   event_date__gte=from_date,
                                                                   event_date__lte=to_date, location_id__in=facilities)
        total_family_planning_referrals = Event.objects.filter(event_type='Family Planning Referral',
                                                               event_date__gte=from_date,
                                                               event_date__lte=to_date, location_id__in=facilities)
        total_family_planning_initiations = Event.objects.filter(event_type='Family Planning Registration',
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
                   'total_anc_referrals': total_anc_referrals.count(),
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

        total_clients = Clients.objects.filter(location_id__in=facilities)
        total_clients_families = Household.objects.filter(location_id__in=facilities)

        total_family_planning_registrations = Event.objects.filter(event_type='Family Planning Registration',
                                                                   location_id__in=facilities)
        total_referrals = Event.objects.filter\
            (Q(event_type='Family Planning Referral') |
             Q(event_type='ANC Referral')).filter(location_id__in = facilities)

        total_family_planning_initiations = Event.objects.filter(event_type='Family Planning Registration',
                                                                 location_id__in=facilities)
        total_family_planning_discontinuations = Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                      location_id__in=facilities)

        content = {'total_services': queryset.count(),
                   'total_clients': total_clients.count(),
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

        willing_to_participate_in_survey_summary = EventExtended.objects.filter\
            (event_type='Citizen Report Card').\
            values('values_1').\
            annotate(value=Count('values_1'))

        name_of_health_facility_visited_for_family_planning_services_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_2'). \
            annotate(value=Count('values_2'))

        residence_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_3'). \
            annotate(value=Count('values_3'))

        education_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_4'). \
            annotate(value=Count('values_4'))

        occupation_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_5'). \
            annotate(value=Count('values_5'))

        marital_status_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_6'). \
            annotate(value=Count('values_6'))

        religion_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_7'). \
            annotate(value=Count('values_7'))

        reasons_for_people_not_going_to_health_facilities_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_8'). \
            annotate(value=Count('values_8'))

        means_of_transport_to_facility_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_9'). \
            annotate(value=Count('values_9'))

        time_to_reach_closest_facility_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_10'). \
            annotate(value=Count('values_10'))

        is_this_the_nearest_facility_from_home_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_11'). \
            annotate(value=Count('values_11'))

        was_the_facility_open_when_you_arrived_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_12'). \
            annotate(value=Count('values_12'))

        did_you_get_family_planning_information_at_the_reception_summary = EventExtended.objects.filter(event_type='Citizen Report Card').values(
            'values_13'). \
            annotate(value=Count('values_13'))

        how_long_it_took_to_be_attended_by_service_provider_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_14'). \
            annotate(value=Count('values_14'))

        did_the_service_provider_make_you_feel_welcome_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_15'). \
            annotate(value=Count('values_15'))

        did_the_service_provider_assure_confidentiality_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_16'). \
            annotate(value=Count('values_16'))

        did_you_meet_the_service_providers_in_a_private_room_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_17'). \
            annotate(value=Count('values_17'))

        did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_18'). \
            annotate(value=Count('values_18'))

        did_the_service_providers_use_visual_aids_to_demo_fp_methods_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_19'). \
            annotate(value=Count('values_19'))

        did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_20'). \
            annotate(value=Count('values_20'))

        were_you_given_info_on_dual_protection_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_21'). \
            annotate(value=Count('values_21'))

        methods_not_wanted_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_22'). \
            annotate(value=Count('values_22'))

        citizen_card_records = EventExtended.objects.filter(event_type='Citizen Report Card')

        converted_citizen_card_report = []

        for x in citizen_card_records:
            willing_to_participate_in_survey = x.values_1
            name_of_health_facility_visited_for_family_planning_services = x.values_2
            residence = x.values_3
            education = x.values_4
            occupation = x.values_5
            marital_status = x.values_6
            religion = x.values_7
            reasons_for_people_not_going_to_health_facilities = x.values_8
            means_of_transport_to_facility = x.values_9
            time_to_reach_closest_facility = x.values_10
            is_this_the_nearest_facility_from_home = x.values_11
            was_the_facility_open_when_you_arrived = x.values_12
            did_you_get_family_planning_information_at_the_reception = x.values_13
            how_long_it_took_to_be_attended_by_service_provider = x.values_14
            did_the_service_provider_make_you_feel_welcome = x.values_15
            did_the_service_provider_assure_confidentiality = x.values_16
            did_you_meet_the_service_providers_in_a_private_room = x.values_17
            did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods = x.values_18
            did_the_service_providers_use_visual_aids_to_demo_fp_methods = x.values_19
            did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods = x.values_20
            were_you_given_info_on_dual_protection = x.values_21
            methods_not_wanted = x.values_22

            converted_citizen_card_report.append({'willing_to_participate_in_survey': willing_to_participate_in_survey,
                                                  'name_of_health_facility_visited_for_family_planning_services':
                                                      name_of_health_facility_visited_for_family_planning_services,
                                                  'residence': residence,
                                                  'education': education,
                                                  'occupation': occupation,
                                                  'marital_status': marital_status,
                                                  'religion': religion,
                                                  'reasons_for_people_not_going_to_health_facilities':
                                                      reasons_for_people_not_going_to_health_facilities,
                                                  'means_of_transport_to_facility': means_of_transport_to_facility,
                                                  'time_to_reach_closest_facility': time_to_reach_closest_facility,
                                                  'is_this_the_nearest_facility_from_home': is_this_the_nearest_facility_from_home,
                                                  'was_the_facility_open_when_you_arrived': was_the_facility_open_when_you_arrived,
                                                  'did_you_get_family_planning_information_at_the_reception':
                                                      did_you_get_family_planning_information_at_the_reception,
                                                  'how_long_it_took_to_be_attended_by_service_provider':
                                                      how_long_it_took_to_be_attended_by_service_provider,
                                                  'did_the_service_provider_make_you_feel_welcome': did_the_service_provider_make_you_feel_welcome,
                                                  'did_the_service_provider_assure_confidentiality': did_the_service_provider_assure_confidentiality,
                                                  'did_you_meet_the_service_providers_in_a_private_room': did_you_meet_the_service_providers_in_a_private_room,
                                                  'did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods':
                                                      did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods,
                                                  'did_the_service_providers_use_visual_aids_to_demo_fp_methods':
                                                      did_the_service_providers_use_visual_aids_to_demo_fp_methods,
                                                  'did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods':
                                                      did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods,
                                                  'were_you_given_info_on_dual_protection': were_you_given_info_on_dual_protection,
                                                  'methods_not_wanted': methods_not_wanted})

        content = {'records':converted_citizen_card_report,
                   'willing_to_participate_in_survey_summary':willing_to_participate_in_survey_summary,
                   'name_of_health_facility_visited_for_family_planning_services_summary':
                       name_of_health_facility_visited_for_family_planning_services_summary,
                   'residence_summary': residence_summary,
                   'education_summary': education_summary,
                   'occupation_summary': occupation_summary,
                   'marital_status_summary': marital_status_summary,
                   'religion_summary': religion_summary,
                   'reasons_for_people_not_going_to_health_facilities_summary':
                       reasons_for_people_not_going_to_health_facilities_summary,
                   'means_of_transport_to_facility_summary': means_of_transport_to_facility_summary,
                   'time_to_reach_closest_facility_summary': time_to_reach_closest_facility_summary,
                   'is_this_the_nearest_facility_from_home_summary': is_this_the_nearest_facility_from_home_summary,
                   'was_the_facility_open_when_you_arrived_summary': was_the_facility_open_when_you_arrived_summary,
                   'did_you_get_family_planning_information_at_the_reception_summary': did_you_get_family_planning_information_at_the_reception_summary,
                   'how_long_it_took_to_be_attended_by_service_provider_summary': how_long_it_took_to_be_attended_by_service_provider_summary,
                   'did_the_service_provider_make_you_feel_welcome_summary': did_the_service_provider_make_you_feel_welcome_summary,
                   'did_the_service_provider_assure_confidentiality_summary': did_the_service_provider_assure_confidentiality_summary,
                   'did_you_meet_the_service_providers_in_a_private_room_summary': did_you_meet_the_service_providers_in_a_private_room_summary,
                   'did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods_summary':
                       did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods_summary,
                   'did_the_service_providers_use_visual_aids_to_demo_fp_methods_summary': did_the_service_providers_use_visual_aids_to_demo_fp_methods_summary,
                   'did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods_summary':
                       did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods_summary,
                   'were_you_given_info_on_dual_protection_summary': were_you_given_info_on_dual_protection_summary,
                   'methods_not_wanted_summary': methods_not_wanted_summary
                   }

        return Response(content)

    def create(self, request, *args, **kwargs):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["start_date"], format_str).date()
        to_date = datetime.strptime(request.data["end_date"], format_str).date()
        facilities = list(request.data["facilities"])

        willing_to_participate_in_survey_summary = EventExtended.objects.filter \
            (event_type='Citizen Report Card', event_date__gte=from_date,
             event_date__lte=to_date, location_id__in=facilities
             ). \
            values('values_1'). \
            annotate(value=Count('values_1'))

        name_of_health_facility_visited_for_family_planning_services_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_2'). \
            annotate(value=Count('values_2'))

        residence_summary = EventExtended.objects.filter(event_type='Citizen Report Card', event_date__gte=from_date,
                                                         event_date__lte=to_date, location_id__in=facilities
                                                         ).values(
            'values_3'). \
            annotate(value=Count('values_3'))

        education_summary = EventExtended.objects.filter(event_type='Citizen Report Card', event_date__gte=from_date,
                                                         event_date__lte=to_date, location_id__in=facilities
                                                         ).values(
            'values_4'). \
            annotate(value=Count('values_4'))

        occupation_summary = EventExtended.objects.filter(event_type='Citizen Report Card', event_date__gte=from_date,
                                                          event_date__lte=to_date, location_id__in=facilities
                                                          ).values(
            'values_5'). \
            annotate(value=Count('values_5'))

        marital_status_summary = EventExtended.objects.filter(event_type='Citizen Report Card',
                                                              event_date__gte=from_date,
                                                              event_date__lte=to_date, location_id__in=facilities
                                                              ).values(
            'values_6'). \
            annotate(value=Count('values_6'))

        religion_summary = EventExtended.objects.filter(event_type='Citizen Report Card', event_date__gte=from_date,
                                                        event_date__lte=to_date, location_id__in=facilities
                                                        ).values(
            'values_7'). \
            annotate(value=Count('values_7'))

        reasons_for_people_not_going_to_health_facilities_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_8'). \
            annotate(value=Count('values_8'))

        means_of_transport_to_facility_summary = EventExtended.objects.filter(event_type='Citizen Report Card',
                                                                              event_date__gte=from_date,
                                                                              event_date__lte=to_date,
                                                                              location_id__in=facilities
                                                                              ).values(
            'values_9'). \
            annotate(value=Count('values_9'))

        time_to_reach_closest_facility_summary = EventExtended.objects.filter(event_type='Citizen Report Card',
                                                                              event_date__gte=from_date,
                                                                              event_date__lte=to_date,
                                                                              location_id__in=facilities
                                                                              ).values(
            'values_10'). \
            annotate(value=Count('values_10'))

        is_this_the_nearest_facility_from_home_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_11'). \
            annotate(value=Count('values_11'))

        was_the_facility_open_when_you_arrived_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_12'). \
            annotate(value=Count('values_12'))

        did_you_get_family_planning_information_at_the_reception_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_13'). \
            annotate(value=Count('values_13'))

        how_long_it_took_to_be_attended_by_service_provider_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_14'). \
            annotate(value=Count('values_14'))

        did_the_service_provider_make_you_feel_welcome_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_15'). \
            annotate(value=Count('values_15'))

        did_the_service_provider_assure_confidentiality_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_16'). \
            annotate(value=Count('values_16'))

        did_you_meet_the_service_providers_in_a_private_room_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_17'). \
            annotate(value=Count('values_17'))

        did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_18'). \
            annotate(value=Count('values_18'))

        did_the_service_providers_use_visual_aids_to_demo_fp_methods_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_19'). \
            annotate(value=Count('values_19'))

        did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_20'). \
            annotate(value=Count('values_20'))

        were_you_given_info_on_dual_protection_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card').values(
            'values_21'). \
            annotate(value=Count('values_21'))

        methods_not_wanted_summary = EventExtended.objects.filter(
            event_type='Citizen Report Card', event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=facilities
        ).values(
            'values_22'). \
            annotate(value=Count('values_22'))

        citizen_card_records = EventExtended.objects.filter(event_type='Citizen Report Card', event_date__gte=from_date,
                                                            event_date__lte=to_date, location_id__in=facilities
                                                            )

        converted_citizen_card_report = []

        for x in citizen_card_records:
            willing_to_participate_in_survey = x.values_1
            name_of_health_facility_visited_for_family_planning_services = x.values_2
            residence = x.values_3
            education = x.values_4
            occupation = x.values_5
            marital_status = x.values_6
            religion = x.values_7
            reasons_for_people_not_going_to_health_facilities = x.values_8
            means_of_transport_to_facility = x.values_9
            time_to_reach_closest_facility = x.values_10
            is_this_the_nearest_facility_from_home = x.values_11
            was_the_facility_open_when_you_arrived = x.values_12
            did_you_get_family_planning_information_at_the_reception = x.values_13
            how_long_it_took_to_be_attended_by_service_provider = x.values_14
            did_the_service_provider_make_you_feel_welcome = x.values_15
            did_the_service_provider_assure_confidentiality = x.values_16
            did_you_meet_the_service_providers_in_a_private_room = x.values_17
            did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods = x.values_18
            did_the_service_providers_use_visual_aids_to_demo_fp_methods = x.values_19
            did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods = x.values_20
            were_you_given_info_on_dual_protection = x.values_21
            methods_not_wanted = x.values_22

            converted_citizen_card_report.append({'willing_to_participate_in_survey': willing_to_participate_in_survey,
                                                  'name_of_health_facility_visited_for_family_planning_services':
                                                      name_of_health_facility_visited_for_family_planning_services,
                                                  'residence': residence,
                                                  'education': education,
                                                  'occupation': occupation,
                                                  'marital_status': marital_status,
                                                  'religion': religion,
                                                  'reasons_for_people_not_going_to_health_facilities':
                                                      reasons_for_people_not_going_to_health_facilities,
                                                  'means_of_transport_to_facility': means_of_transport_to_facility,
                                                  'time_to_reach_closest_facility': time_to_reach_closest_facility,
                                                  'is_this_the_nearest_facility_from_home': is_this_the_nearest_facility_from_home,
                                                  'was_the_facility_open_when_you_arrived': was_the_facility_open_when_you_arrived,
                                                  'did_you_get_family_planning_information_at_the_reception':
                                                      did_you_get_family_planning_information_at_the_reception,
                                                  'how_long_it_took_to_be_attended_by_service_provider':
                                                      how_long_it_took_to_be_attended_by_service_provider,
                                                  'did_the_service_provider_make_you_feel_welcome': did_the_service_provider_make_you_feel_welcome,
                                                  'did_the_service_provider_assure_confidentiality': did_the_service_provider_assure_confidentiality,
                                                  'did_you_meet_the_service_providers_in_a_private_room': did_you_meet_the_service_providers_in_a_private_room,
                                                  'did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods':
                                                      did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods,
                                                  'did_the_service_providers_use_visual_aids_to_demo_fp_methods':
                                                      did_the_service_providers_use_visual_aids_to_demo_fp_methods,
                                                  'did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods':
                                                      did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods,
                                                  'were_you_given_info_on_dual_protection': were_you_given_info_on_dual_protection,
                                                  'methods_not_wanted': methods_not_wanted})

        content = {'records': converted_citizen_card_report,
                   'willing_to_participate_in_survey_summary': willing_to_participate_in_survey_summary,
                   'name_of_health_facility_visited_for_family_planning_services_summary':
                       name_of_health_facility_visited_for_family_planning_services_summary,
                   'residence_summary': residence_summary,
                   'education_summary': education_summary,
                   'occupation_summary': occupation_summary,
                   'marital_status_summary': marital_status_summary,
                   'religion_summary': religion_summary,
                   'reasons_for_people_not_going_to_health_facilities_summary':
                       reasons_for_people_not_going_to_health_facilities_summary,
                   'means_of_transport_to_facility_summary': means_of_transport_to_facility_summary,
                   'time_to_reach_closest_facility_summary': time_to_reach_closest_facility_summary,
                   'is_this_the_nearest_facility_from_home_summary': is_this_the_nearest_facility_from_home_summary,
                   'was_the_facility_open_when_you_arrived_summary': was_the_facility_open_when_you_arrived_summary,
                   'did_you_get_family_planning_information_at_the_reception_summary': did_you_get_family_planning_information_at_the_reception_summary,
                   'how_long_it_took_to_be_attended_by_service_provider_summary': how_long_it_took_to_be_attended_by_service_provider_summary,
                   'did_the_service_provider_make_you_feel_welcome_summary': did_the_service_provider_make_you_feel_welcome_summary,
                   'did_the_service_provider_assure_confidentiality_summary': did_the_service_provider_assure_confidentiality_summary,
                   'did_you_meet_the_service_providers_in_a_private_room_summary': did_you_meet_the_service_providers_in_a_private_room_summary,
                   'did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods_summary':
                       did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods_summary,
                   'did_the_service_providers_use_visual_aids_to_demo_fp_methods_summary': did_the_service_providers_use_visual_aids_to_demo_fp_methods_summary,
                   'did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods_summary':
                       did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods_summary,
                   'were_you_given_info_on_dual_protection_summary': were_you_given_info_on_dual_protection_summary,
                   'methods_not_wanted_summary': methods_not_wanted_summary
                   }

        return Response(content)


class FamilyPlanningMethodView(viewsets.ModelViewSet):
    queryset = EventExtended.objects.filter(event_type="Give Family Planning Method")
    serializer_class=  EventsSerializer
    permission_classes = ()

    def list(self, request):
        pop_given= EventExtended.objects.filter(event_type='Give Family Planning Method',field_code_3='pop_given',
                                                                    values_2="true")

        coc_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                      field_code_3='coc_given',
                                                      values_2="true")
        sdm_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                      field_code_3='sdm_given',
                                                      values_2="true")

        content = []

        total_pop_given = 0
        total_coc_given = 0
        total_sdm_given = 0

        for x in pop_given:
            total_pop_given += int(x.values_4)

        for x in coc_given:
            total_coc_given += int(x.values_4)

        for x in sdm_given:
            total_sdm_given += int(x.values_4)

        content.append({"method_type": "pop_given", "number_of_items": total_pop_given})
        content.append({"method_type": "coc_given", "number_of_items": total_coc_given})
        content.append({"method_type": "sdm_given", "number_of_item": total_sdm_given})

        return Response(content)

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = list(request.data["facilities"])

        pop_given = EventExtended.objects.filter(event_type='Give Family Planning Method', field_code_3='pop_given',
                                                 values_2="true", event_date__gte=from_date,
                                                 event_date__lte=to_date, location_id__in=facilities
                                                 )

        coc_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                 field_code_3='coc_given',
                                                 values_2="true", event_date__gte=from_date,
                                                 event_date__lte=to_date, location_id__in=facilities
                                                 )
        sdm_given = EventExtended.objects.filter(event_type='Give Family Planning Method',
                                                 field_code_3='sdm_given',
                                                 values_2="true", event_date__gte=from_date,
                                                 event_date__lte=to_date, location_id__in=facilities
                                                 )

        content = []

        total_pop_given = 0
        total_coc_given = 0
        total_sdm_given = 0

        for x in pop_given:
            total_pop_given += int(x.values_4)

        for x in coc_given:
            total_coc_given += int(x.values_4)

        for x in sdm_given:
            total_sdm_given += int(x.values_4)

        content.append({"method_type": "pop given", "number_of_items": total_pop_given})
        content.append({"method_type": "coc given", "number_of_items": total_coc_given})
        content.append({"method_type": "sdm given", "number_of_item": total_sdm_given})

        return Response(content)


class MapSummaryView(viewsets.ModelViewSet):
    queryset = EventExtended.objects.filter(event_type="Family Planning Registration")
    serializer_class= EventsSerializer
    permission_classes = ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        services = {
                    1:'Family Planning Registration',
                    2: 'Family Planning Follow Up Visit',
                    4: 'Family Planning Pregnancy Screening',
                    3: 'Introduction to Family Planning',
                    5: 'Family Planning Method Issued',
                    6: 'Family Planning Discontinuation',
                    7: 'ANC Referral',
                    8: 'Family Planning Referral',
                    9: 'Family Planning Referral Followup'
                    }

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = list(request.data["facilities"])
        org_units = list(request.data["orgUnits"])
        selected_location_name = request.data["ouName"]
        service_id = request.data["service"]
        selected_service = services[service_id]
        content = []

        total_value = 0

        # need to find what villag each facility belongs to
        for facility in facilities:
            for unit in org_units:
                if unit["id"] == facility and unit["level"] == 4:

                    village_name = unit["name"]
                    query_events = EventExtended.objects.filter(event_date__gte=from_date,
                                                                event_date__lte=to_date, location_id=facility,
                                                                event_type='' + selected_service + ''
                                                                ).values('event_type').annotate(value=Count('event_type'))
                    for x in query_events:
                        total_value += int(x['value'])

                    village_data = {"village_name": village_name, "value": total_value}

                    # Initialize count for new facility
                    total_value = 0

                    content.append(village_data)
                elif unit["id"] == facility:

                    split_string = unit["parents"].split(';', -1)
                    last_parent = str(split_string[-1])

                    for x in org_units:
                        if last_parent == x["id"]:
                            village_name = x["name"]

                            query_events = EventExtended.objects.filter(event_date__gte=from_date,
                                                                        event_date__lte=to_date, location_id=facility,
                                                                        event_type='' + selected_service + ''
                                                                        ).values('event_type').annotate(
                                value=Count('event_type'))

                            for x in query_events:
                                total_value += int(x['value'])

                            village_data = {"village_name": village_name, "value": total_value}

                            # Initialize count for new facility
                            total_value = 0

                            content.append(village_data)

        return Response(content)















