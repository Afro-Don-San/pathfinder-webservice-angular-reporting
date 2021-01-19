from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser, AllowAny
from django.db.models import Count, Sum
from django.conf import settings
from .serializers import EventsSerializer,DashboardSummarySerializer, \
    ReferralTaskSerializer, CloseReferralSerializer, HouseholdSerializer, ClientsSerializer, GiveFpMethodSerializer, CitizenReportCardSerializer
from .models import Event, Client, Clients, Household, ReferralTask, CitizenReportCard, GiveFpMethod,CloseReferral, TeamMembers
import requests
from datetime import datetime
from django.db import models
from django.db.models import Func, Q
from django.db.models.functions import TruncMonth, ExtractMonth
from dateutil.relativedelta import relativedelta
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

        # Fetch referrals by chw
        referral_issued_by_chw = ReferralTask.objects.filter(execution_start_date__gte=from_date,
                                                             execution_start_date__lte=to_date,
                                                             health_facility_location_id__in=locations). \
            values('chw_id', 'chw_name').annotate(value=Count('chw_id'))

        json_array_chw = []
        json_array_total = []

        for x in referral_issued_by_chw:
            query_completed_referrals = ReferralTask.objects.filter(execution_start_date__gte=from_date,
                                                                    execution_start_date__lte=to_date,
                                                                    health_facility_location_id__in=locations
                                                                    ,chw_id=x['chw_id'], businessstatus='Complete')
            referral_object = {'chw_id': x['chw_id'], 'chw_name': x['chw_name'], 'issued': x['value'],
                               'completed': query_completed_referrals.count()}

            json_array_chw.append(referral_object)


        # Fetch referrals by type
        referral_total = ReferralTask.objects.filter(execution_start_date__gte=from_date,
                                                     execution_start_date__lte=to_date,
                                                     health_facility_location_id__in=locations). \
            values('focus').annotate(value=Count('focus'))

        for y in referral_total:
            query_completed_referrals = ReferralTask.objects.filter(execution_start_date__gte=from_date,
                                                                    execution_start_date__lte=to_date,
                                                                    health_facility_location_id__in=locations, businessstatus='Complete',
                                                                    focus=y['focus'])

            referral_object = {'focus': y['focus'], 'issued': y['value'],
                               'completed': query_completed_referrals.count()}

            json_array_total.append(referral_object)

        content = {'referral_types_focus': referral_types_focus,
                   'referral_status': referral_status,
                   'referral_issued_by_chw': json_array_chw,
                   'referral_issued_total': json_array_total
                   }

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

        chw_array = []

        clients = Clients.objects.filter(event_date__gte=from_date,
                                         event_date__lte=to_date,
                                         location_id__in=locations).values('first_name', 'middle_name', 'last_name',
                                                                           'gender', 'phone_number', 'birth_date')
        client_registration_by_month = Clients.objects.filter(event_date__gte=from_date,
                                                              event_date__lte=to_date, location_id__in=locations
                                                              ).annotate(
            month_number=ExtractMonth('event_date'),
        ).values('month_number').annotate(
            value=Count('id')).order_by('month_number')

        client_registration_by_chw = Clients.objects.filter(event_date__gte=from_date,
                                                            event_date__lte=to_date, location_id__in=locations
                                                            ).values('provider_id').annotate(value=Count('provider_id'))\
            .order_by('-value')

        for client in client_registration_by_chw:
            chw_id = client['provider_id']

            try:
                instance_team_member = TeamMembers.objects.get(identifier = chw_id)
                chw_name = instance_team_member.name
            except:
                chw_name = 'NIL'

            chw_object = {"chw_name": chw_name, "chw_id":chw_id,
                          "value":client['value']}

            chw_array.append(chw_object)

        for x in client_registration_by_month:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_client_registration_by_month.append({'month_name': month_name, 'value': month_value})

        content = {'clients': clients,
                   'client_registration_by_month': converted_client_registration_by_month,
                   'client_registrations_by_chw': chw_array}

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

        total_visits = Event.objects.filter(location_id__in=facilities).filter(Q(event_type='Fp Follow Up Visit') |
                                                                               Q(event_type='Family Planning Method Referral Followup')|
                                                                               Q(event_type='Family Planning Pregnancy Test Referral Followup')).values('event_type')


        content = {'total_services': queryset.count(),
                   'total_clients': total_clients.count(),
                   'total_visits': total_visits.count(),
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
                                                       event_date__lte=to_date, location_id__in=facilities).annotate(
            month_number=ExtractMonth('date_created'),
        ).values('month_number').annotate(
            value=Count('id')
        ).order_by('month_number')

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
            value=Count('id')).order_by('month_number')

        for x in family_planning_initiations:
            month_number = int(x['month_number'])
            month_value = x['value']
            month_name = calendar.month_name[month_number]

            converted_family_planning_initiations.append({'month_name': month_name, 'value': month_value})

        # Discontinuations
        family_planning_discontinuations = total_family_planning_discontinuations.annotate(
            month_number=ExtractMonth('event_date'),
        ).values('month_number').annotate(
            value=Count('id')).order_by('month_number')

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

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        locations = list(request.data["facilities"])

        query_wait_time = CitizenReportCard.objects.filter(event_date__gte=from_date, event_date__lte=to_date,
                                                           location_id__in=locations). \
            values('how_long_it_took_to_be_attended_by_service_provider').annotate \
            (value=Count('how_long_it_took_to_be_attended_by_service_provider'))

        query_attempts_complete = CitizenReportCard.objects.filter(event_date__gte=from_date, event_date__lte=to_date,
                                                                   location_id__in=locations). \
            values('times_the_client_tried_to_complete_referral').annotate \
            (value=Count('times_the_client_tried_to_complete_referral'))

        query_reason_not_getting_service= CitizenReportCard.objects.filter(event_date__gte=from_date, event_date__lte=to_date,
                                                                           location_id__in=locations). \
            values('reasons_for_not_getting_services').annotate \
            (value=Count('reasons_for_not_getting_services'))

        query_amount_asked_to_pay = CitizenReportCard.objects.filter(event_date__gte=from_date,
                                                                     event_date__lte=to_date,
                                                                     location_id__in=locations). \
            values('amount_asked_to_pay_for_services').annotate \
            (value=Count('amount_asked_to_pay_for_services'))


        content = {
            "wait_time": query_wait_time,
            "attempts_complete": query_attempts_complete,
            "reason_not_getting_service": query_reason_not_getting_service,
            "amount_asked_to_pay_for_services": query_amount_asked_to_pay
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
        content.append({"method_type": "male condoms", "items": total_male_condoms})

        # total clients
        content_clients.append({"method_type": "pop given", "clients": pop_given.count()})
        content_clients.append({"method_type": "coc given", "clients": coc_given.count()})
        content_clients.append({"method_type": "male condoms", "clients": male_condoms.count()})

        json_array = {
            "total_fp_methods" : content,
            "total_clients" : content_clients
        }

        return Response(json_array)


class VisitTypesView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer
    permission_classes = ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        locations = list(request.data["facilities"])

        query_followups = Event.objects.filter(event_date__gte=from_date,
                                               event_date__lte=to_date, location_id__in=locations
                                               ).filter(Q(event_type = 'Fp Follow Up Visit') |
                                                        Q(event_type = 'Family Planning Method Referral Followup') |
                                                        Q(event_type='Family Planning Pregnancy Test Referral Followup') |
                                                        Q(event_type='Family Planning Method Refill Referral Followup')). \
            values('event_type').annotate(
            value=Count('event_type'))


        content = {"total_fp_visits": query_followups}

        return Response(content)


class CloseReferralView(viewsets.ModelViewSet):
    queryset = CloseReferral.objects.all()
    serializer_class = CloseReferralSerializer
    permission_classes = ()

    def create(self, request):
        format_str = '%Y/%m/%d'  # The format

        from_date = datetime.strptime(request.data["from_date"], format_str).date()
        to_date = datetime.strptime(request.data["to_date"], format_str).date()
        locations = list(request.data["facilities"])

        query_service_provided = CloseReferral.objects.filter(event_date__gte=from_date,
                                                              event_date__lte=to_date, location_id__in=locations
                                                              ).values('service_provided').annotate(value=Count('service_provided'))

        methods_disaggregated = []

        for x in query_service_provided:
            # client metadata has base_entty_id as client id
            query_selected_method = CloseReferral.objects.filter(event_date__gte=from_date,
                                                                 event_date__lte=to_date, location_id__in=locations,
                                                                 service_provided = ""+x['service_provided']+"")
            now = datetime.now()

            total_female_10_14 = 0
            total_female_15_19 = 0
            total_female_20_24 = 0
            total_female_25_ = 0

            total_male_10_14 = 0
            total_male_15_19 = 0
            total_male_20_24 = 0
            total_male_25_ = 0

            for y in query_selected_method:
                query_client = Clients.objects.get(base_entity_id=y.base_entity_id)
                client_birth_date = query_client.birth_date
                client_gender = query_client.gender
                difference = relativedelta(now, client_birth_date)
                age_in_years = difference.years

                if 10 <= age_in_years <= 14:
                    if client_gender == 'Female':
                        total_female_10_14 +=1
                    elif client_gender == 'Male':
                        total_male_10_14 += 1

                if 15 <= age_in_years <= 19:
                    if client_gender == 'Female':
                        total_female_15_19 += 1
                    elif client_gender == 'Male':
                        total_male_15_19 += 1

                if 20 <= age_in_years <= 24:
                    if client_gender == 'Female':
                        total_female_20_24 += 1
                    elif client_gender == 'Male':
                        total_male_20_24 += 1

                if age_in_years >= 25:
                    if client_gender == 'Female':
                        total_female_25_ += 1
                    elif client_gender == 'Male':
                        total_male_25_ += 1

            methods_disaggregated.append({"method":x['service_provided'], "total_female_10_14":total_female_10_14,
                                          "total_female_15_19": total_female_15_19, "total_female_20_24":total_female_20_24,
                                          "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                          "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                          "total_male_25_": total_male_25_})

        content = {"service_provided": query_service_provided,
                   "methods_disaggregated": methods_disaggregated}

        return Response(content)
























