from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count, Sum
from django.conf import settings
from .serializers import EventsSerializer,DashboardSummarySerializer, \
    ReferralTaskSerializer, HouseholdSerializer, ClientsSerializer, GiveFpMethodSerializer, CitizenReportCardSerializer
from .models import Event, Client, Clients, Household, ReferralTask, CitizenReportCard, GiveFpMethod
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


class MapSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.filter(event_type="Family Planning Registration")
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
                    query_events = Event.objects.filter(event_date__gte=from_date,
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

                            query_events = Event.objects.filter(event_date__gte=from_date,
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


# Revised functions
class ReferralTaskView(viewsets.ModelViewSet):
    queryset = ReferralTask.objects.all()
    serializer_class  = ReferralTaskSerializer
    permission_classes =  ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        locations = list(request.data["facilities"])

        referral_status = ReferralTask.objects.filter(execution_start_date__gte=from_date,
                                                      execution_start_date__lte=to_date,
                                                      health_facility_location_id__in=locations). \
            values('businessstatus').annotate(value=Count('businessstatus'))

        referral_types_focus = ReferralTask.objects.filter(execution_start_date__gte=from_date,
                                                           execution_start_date__lte=to_date,
                                                           health_facility_location_id__in=locations). \
            values('focus').annotate(value=Count('focus'))

        referral_issued_by_chw = ReferralTask.objects.filter(execution_start_date__gte=from_date,
                                                             execution_start_date__lte=to_date,
                                                             health_facility_location_id__in=locations). \
            values('chw_id', 'chw_name').annotate(value=Count('chw_id'))

        content = {'referral_types_focus': referral_types_focus,
                   'referral_status': referral_status,
                   'referral_issued_by_chw': referral_issued_by_chw}

        return Response(content)


class ClientsView(viewsets.ModelViewSet):
    queryset = Clients.objects.all()
    serializer_class = ClientsSerializer
    permission_classes = ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        converted_client_registration_by_month = []

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        locations = list(request.data["facilities"])

        clients = Clients.objects.filter(event_date__gte=from_date,
                                         event_date__lte=to_date,
                                         location_id__in=locations).values('first_name', 'middle_name', 'last_name',
                                                                           'gender', 'phone_number', 'birth_date')
        client_registration_by_month = Clients.objects.filter(event_date__gte=from_date,
                                                              event_date__lte=to_date, location_id__in=locations
                                                              ).annotate(
            month_number=ExtractMonth('event_date'),
        ).values('month_number').annotate(
            value=Count('id')
        )

        for x in client_registration_by_month:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_client_registration_by_month.append({'month_name': month_name, 'value': month_value})

        print(converted_client_registration_by_month)

        content = {'clients': clients,
                   'client_registration_by_month': converted_client_registration_by_month}

        return Response(content)


class DashboardSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = DashboardSummarySerializer
    permission_classes = ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        facilities = request.data["facilities"]

        queryset = Event.objects.filter(location_id__in=facilities)

        total_clients = Clients.objects.filter(location_id__in=facilities)
        total_clients_families = Household.objects.filter(location_id__in=facilities)

        total_referrals = ReferralTask.objects.filter(health_facility_location_id__in=facilities)

        total_family_planning_initiations = Event.objects.filter(event_type='Family Planning Registration',
                                                                 location_id__in=facilities)
        total_family_planning_discontinuations = Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                      location_id__in=facilities)

        total_citizen_reports = Event.objects.filter(event_type='Citizen Report Card',
                                                     location_id__in=facilities)

        content = {'total_services': queryset.count(),
                   'total_clients': total_clients.count(),
                   'total_referrals': total_referrals.count(),
                   'total_family_planning_initiations': total_family_planning_initiations.count(),
                   'total_family_planning_discontinuations': total_family_planning_discontinuations.count(),
                   'total_clients_families': total_clients_families.count(),
                   'total_citizen_reports': total_citizen_reports.count()}
        return Response(content)


class EventsSummaryView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        facilities = list(request.data["facilities"])

        converted_family_planning_initiations = []
        converted_family_planning_discontinuations = []

        queryset = Event.objects.filter(event_date__gte=from_date,
                                        event_date__lte=to_date, location_id__in=facilities)
        query_service_providers = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date, location_id__in=facilities).values(
            'team').distinct()

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
        total_family_planning_registrations_by_team = Event.objects.filter(
            event_type='Family Planning Registration',
            event_date__gte=from_date,
            event_date__lte=to_date,
            location_id__in=facilities
        ). \
            values('team_id').annotate(value=Count('team_id'))

        total_issued_referrals = Event.objects.filter(event_date__gte=from_date,
                                                      event_date__lte=to_date, location_id__in=facilities). \
            filter(Q(event_type='ANC Referral') | Q(event_type='Family Planning Referral')
                   | Q(event_type='Family Planning Referral Followup')).values('event_type'). \
            annotate(value=Count('event_type'))

        serializer = EventsSerializer(queryset, many=True)
        total_services_aggregate = Event.objects.filter(event_date__gte=from_date,
                                                        event_date__lte=to_date, location_id__in=facilities). \
            values('event_type').annotate(value=Count('event_type'))
        total_services_by_month = Event.objects.filter(event_date__gte=from_date,
                                                       event_date__lte=to_date, location_id__in=facilities
                                                       ).annotate(
            month_number=ExtractMonth('date_created'),
        ).values('month_number').annotate(
            value=Count('id')
        )


        converted_total_services_by_month = []

        for x in total_services_by_month:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_total_services_by_month.append({'month_name': month_name, 'value': month_value})


        # Initiations and Discontinuations by Month
        # Initiations
        family_planning_initiations = total_family_planning_initiations.annotate(
            month_number=ExtractMonth('event_date'),
        ).values('month_number').annotate(
            value=Count('id')
        )

        for x in family_planning_initiations:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_family_planning_initiations.append({'month_name': month_name, 'value': month_value})

        # Discontinuations
        family_planning_discontinuations = total_family_planning_discontinuations.annotate(
            month_number=ExtractMonth('event_date'),
        ).values('month_number').annotate(
            value=Count('id')
        )

        for x in family_planning_discontinuations:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_family_planning_discontinuations.append({'month_name': month_name, 'value': month_value})

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
                   'family_planning_initiations': converted_family_planning_initiations,
                   'family_planning_discontinuations': converted_family_planning_discontinuations,
                   'records': serializer.data}
        return Response(content)


class CitizenReportCardView(viewsets.ModelViewSet):
    queryset = CitizenReportCard.objects.all()
    serializer_class=  CitizenReportCardSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["start_date"], format_str).date()
        to_date = datetime.strptime(request.data["end_date"], format_str).date()
        locations = list(request.data["facilities"])

        willing_to_participate_in_survey_summary = CitizenReportCard.objects.filter \
            (event_date__gte=from_date,
             event_date__lte=to_date, location_id__in=locations
             ). \
            values('willing_to_participate_in_survey'). \
            annotate(value=Count('willing_to_participate_in_survey'))
        print(willing_to_participate_in_survey_summary)

        name_of_health_facility_visited_for_family_planning_services_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'name_of_health_facility_visited_for_family_planning_services'). \
            annotate(value=Count('name_of_health_facility_visited_for_family_planning_services'))

        residence_summary = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                             event_date__lte=to_date, location_id__in=locations
                                                             ).values(
            'residence'). \
            annotate(value=Count('residence'))

        education_summary = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                             event_date__lte=to_date, location_id__in=locations
                                                             ).values(
            'education'). \
            annotate(value=Count('education'))

        occupation_summary = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                              event_date__lte=to_date, location_id__in=locations
                                                              ).values(
            'occupation'). \
            annotate(value=Count('occupation'))

        marital_status_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'marital_status'). \
            annotate(value=Count('marital_status'))

        religion_summary = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                            event_date__lte=to_date, location_id__in=locations
                                                            ).values(
            'religion'). \
            annotate(value=Count('religion'))

        reasons_for_people_not_going_to_health_facilities_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'reasons_for_people_not_going_to_health_facilities'). \
            annotate(value=Count('reasons_for_people_not_going_to_health_facilities'))

        means_of_transport_to_facility_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date,
            location_id__in=locations
        ).values(
            'means_of_transport_to_facility'). \
            annotate(value=Count('means_of_transport_to_facility'))

        time_to_reach_closest_facility_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date,
            location_id__in=locations
        ).values(
            'time_to_reach_facility_closest_from_household'). \
            annotate(value=Count('time_to_reach_facility_closest_from_household'))

        is_this_the_nearest_facility_from_home_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'is_this_the_nearest_facility_from_home'). \
            annotate(value=Count('is_this_the_nearest_facility_from_home'))

        was_the_facility_open_when_you_arrived_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'was_the_facility_open_when_you_arrived'). \
            annotate(value=Count('was_the_facility_open_when_you_arrived'))

        did_you_get_family_planning_information_at_the_reception_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_you_get_family_planning_information_at_the_reception'). \
            annotate(value=Count('did_you_get_family_planning_information_at_the_reception'))

        how_long_it_took_to_be_attended_by_service_provider_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations).values(
            'how_long_it_took_to_be_attended_by_service_provider'). \
            annotate(value=Count('how_long_it_took_to_be_attended_by_service_provider'))

        did_the_service_provider_make_you_feel_welcome_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_the_service_provider_make_you_feel_welcome'). \
            annotate(value=Count('did_the_service_provider_make_you_feel_welcome'))

        did_the_service_provider_assure_confidentiality_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_the_service_provider_assure_confidentiality'). \
            annotate(value=Count('did_the_service_provider_assure_confidentiality'))

        did_you_meet_the_service_providers_in_a_private_room_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_you_meet_the_service_providers_in_a_private_room'). \
            annotate(value=Count('did_you_meet_the_service_providers_in_a_private_room'))

        did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_the_providers_give_clear_info_about_services_and_methods'). \
            annotate(value=Count('did_the_providers_give_clear_info_about_services_and_methods'))

        did_the_service_providers_use_visual_aids_to_demo_fp_methods_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_the_service_providers_use_visual_aids_to_demo_fp_methods'). \
            annotate(value=Count('did_the_service_providers_use_visual_aids_to_demo_fp_methods'))

        did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_the_providers_ask_of_any_concerns_about_used_methods'). \
            annotate(value=Count('did_the_providers_ask_of_any_concerns_about_used_methods'))

        were_you_given_info_on_dual_protection_summary = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                                                          event_date__lte=to_date,
                                                                                          location_id__in=locations
                                                                                          ).values(
            'were_you_given_info_on_dual_protection'). \
            annotate(value=Count('were_you_given_info_on_dual_protection'))

        did_you_pay_for_the_service_summary = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                                               event_date__lte=to_date, location_id__in=locations
                                                                               ).values(
            'did_you_pay_for_the_service'). \
            annotate(value=Count('did_you_pay_for_the_service'))

        were_you_asked_to_give_some_kickbacks_to_get_the_service_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'were_you_asked_to_give_some_kickbacks_to_get_the_service'). \
            annotate(value=Count('were_you_asked_to_give_some_kickbacks_to_get_the_service'))

        why_did_you_not_get_the_services_at_the_health_facility_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'why_did_you_not_get_the_services_at_the_health_facility'). \
            annotate(value=Count('why_did_you_not_get_the_services_at_the_health_facility'))

        did_you_file_a_complaint_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'did_you_file_a_complaint'). \
            annotate(value=Count('did_you_file_a_complaint'))

        will_you_go_back_for_fp_services_at_this_facility_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'will_you_go_back_for_fp_services_at_this_facility'). \
            annotate(value=Count('will_you_go_back_for_fp_services_at_this_facility'))

        are_you_satisfied_with_fp_services_provided_using_phone_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'are_you_satisfied_with_fp_services_provided_using_phone'). \
            annotate(value=Count('are_you_satisfied_with_fp_services_provided_using_phone'))

        have_fp_services_improved_summary = CitizenReportCard.objects.filter(
            event_date__gte=from_date,
            event_date__lte=to_date, location_id__in=locations
        ).values(
            'have_fp_services_improved'). \
            annotate(value=Count('have_fp_services_improved'))

        citizen_card_records = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                                event_date__lte=to_date, location_id__in=locations
                                                                )

        converted_citizen_card_report = []

        for x in citizen_card_records:
            willing_to_participate_in_survey = x.willing_to_participate_in_survey
            name_of_health_facility_visited_for_family_planning_services = x.name_of_health_facility_visited_for_family_planning_services
            residence = x.residence
            education = x.education
            occupation = x.occupation
            marital_status = x.marital_status
            religion = x.religion
            reasons_for_people_not_going_to_health_facilities = x.reasons_for_people_not_going_to_health_facilities
            means_of_transport_to_facility = x.means_of_transport_to_facility
            time_to_reach_closest_facility = x.time_to_reach_facility_closest_from_household
            is_this_the_nearest_facility_from_home = x.is_this_the_nearest_facility_from_home
            was_the_facility_open_when_you_arrived = x.was_the_facility_open_when_you_arrived
            did_you_get_family_planning_information_at_the_reception = x.did_you_get_family_planning_information_at_the_reception
            how_long_it_took_to_be_attended_by_service_provider = x.how_long_it_took_to_be_attended_by_service_provider
            did_the_service_provider_make_you_feel_welcome = x.did_the_service_provider_make_you_feel_welcome
            did_the_service_provider_assure_confidentiality = x.did_the_service_provider_assure_confidentiality
            did_you_meet_the_service_providers_in_a_private_room = x.did_you_meet_the_service_providers_in_a_private_room
            did_the_service_providers_provide_clear_information_about_various_fp_services_and_methods = \
                x.did_the_providers_give_clear_info_about_services_and_methods
            did_the_service_providers_use_visual_aids_to_demo_fp_methods = x.did_the_service_providers_use_visual_aids_to_demo_fp_methods
            did_the_service_providers_ask_if_you_had_any_concerns_about_previously_used_methods = x.did_the_providers_ask_of_any_concerns_about_used_methods
            were_you_given_info_on_dual_protection = x.were_you_given_info_on_dual_protection
            did_you_file_a_complaint = x.did_you_file_a_complaint
            will_you_go_back_for_fp_services_at_this_facility = x.will_you_go_back_for_fp_services_at_this_facility
            are_you_satisfied_with_fp_services_provided_using_phone = x.are_you_satisfied_with_fp_services_provided_using_phone
            have_fp_services_improved = x.have_fp_services_improved
            why_did_you_not_get_the_services_at_the_health_facility = x.why_did_you_not_get_the_services_at_the_health_facility

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
                                                  'did_you_file_a_complaint': did_you_file_a_complaint,
                                                  'will_you_go_back_for_fp_services_at_this_facility': will_you_go_back_for_fp_services_at_this_facility,
                                                  'are_you_satisfied_with_fp_services_provided_using_phone': are_you_satisfied_with_fp_services_provided_using_phone,
                                                  'have_fp_services_improved': have_fp_services_improved,
                                                  'why_did_you_not_get_the_services_at_the_health_facility': why_did_you_not_get_the_services_at_the_health_facility

                                                  })

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
                   'did_you_pay_for_the_service_summary': did_you_pay_for_the_service_summary,
                   'why_did_you_not_get_the_services_at_the_health_facility_summary': why_did_you_not_get_the_services_at_the_health_facility_summary,
                   'did_you_file_a_complaint_summary': did_you_file_a_complaint_summary,
                   'will_you_go_back_for_fp_services_at_this_facility_summary': will_you_go_back_for_fp_services_at_this_facility_summary,
                   'are_you_satisfied_with_fp_services_provided_using_phone_summary': are_you_satisfied_with_fp_services_provided_using_phone_summary,
                   'were_you_asked_to_give_some_kickbacks_to_get_the_service_summary': were_you_asked_to_give_some_kickbacks_to_get_the_service_summary,
                   'have_fp_services_improved_summary': have_fp_services_improved_summary

                   }

        return Response(content)


class FamilyPlanningMethodView(viewsets.ModelViewSet):
    queryset = GiveFpMethod.objects.all()
    serializer_class = GiveFpMethodSerializer
    permission_classes = ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        locations = list(request.data["facilities"])

        pop_given = GiveFpMethod.objects.filter(
            pop_given='yes',
            date_created__gte=from_date,
            date_created__lte=to_date, location_id__in=locations
        )

        coc_given = GiveFpMethod.objects.filter(
            coc_given='yes',
            date_created__gte=from_date,
            date_created__lte=to_date, location_id__in=locations
        )
        sdm_given = GiveFpMethod.objects.filter(
            sdm_given='yes',
            date_created__gte=from_date,
            date_created__lte=to_date, location_id__in=locations
        )

        male_condoms = GiveFpMethod.objects.filter(
            male_condoms_given='yes',
            date_created__gte=from_date,
            date_created__lte=to_date, location_id__in=locations
        )

        content = []
        content_clients = []
        json_array = []

        total_pop_given = 0
        total_coc_given = 0
        total_sdm_given = 0
        total_male_condoms = 0

        for x in pop_given:
            total_pop_given += int(x.number_of_pills)

        for x in coc_given:
            total_coc_given += int(x.number_of_pills)

        for x in sdm_given:
            total_sdm_given += int(x.number_of_pills)

        for x in male_condoms:
            total_male_condoms += int(x.number_of_condoms)

        # total fp
        content.append({"method_type": "pop given", "items": total_pop_given})
        content.append({"method_type": "coc given", "items": total_coc_given})
        content.append({"method_type": "sdm given", "items": total_sdm_given})
        content.append({"method_type": "male condoms", "items": total_male_condoms})

        # total clients
        content_clients.append({"method_type": "pop given", "clients": pop_given.count()})
        content_clients.append({"method_type": "coc given", "clients": coc_given.count()})
        content_clients.append({"method_type": "sdm given", "clients": sdm_given.count()})
        content_clients.append({"method_type": "male condoms", "clients": male_condoms.count()})

        json_array = {
                        "total_fp_methods" : content,
                        "total_clients" : content_clients
                      }

        return Response(json_array)
























