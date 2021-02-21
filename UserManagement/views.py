from django.conf import settings
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from Core import models as core_models
from Core import views as core_views
from .tables import TeamTable, LocationTable, ClientsTable
from django.db.models import Count
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Func, Q
from django.core import serializers
import xlwt
import json
from datetime import date
from dateutil.relativedelta import relativedelta

# Create your views here.
def get_login_page(request):
    return render(request, 'UserManagement/Auth/Login.html')


def get_geo_maps_page(request):
    content = core_views.get_dashboard_summary(request)
    return render(request, 'UserManagement/Features/Geomaps.html', {
        'total_clients': content['total_clients'],
        'total_referrals': content[
            'total_referrals'],
        'total_visits': content['total_visits'],
        'total_family_planning_initiations':
            content[
                'total_family_planning_initiations'],
        'total_family_planning_discontinuations':
            content[
                'total_family_planning_discontinuations'],
        'total_citizen_reports': content[
            'total_citizen_reports']
    })


def get_location_management_page(request):
    locations = core_models.Location.objects.all().order_by('location_id')
    locations_table = LocationTable(locations)
    RequestConfig(request, paginate={"per_page": 10}).configure(locations_table)
    return render(request, 'UserManagement/Features/LocationManagement.html', {"locations_table":locations_table})


def get_team_management_page(request):
    teams = core_models.Team.objects.all().order_by('team_id')
    teams_table = TeamTable(teams)
    RequestConfig(request, paginate={"per_page": 10}).configure(teams_table)
    return render(request, 'UserManagement/Features/TeamManagement.html',{'teams_table':teams_table})


def get_locations(request):
    locations = core_models.Location.objects.all().order_by('location_id')
    location_array = []

    for x in locations:
        location = {"name":x.name, "description":x.description, "parent": x.parent_location}
        location_array.append(location)

    # locations_json = serializers.serialize('json', location_array)
    return HttpResponse(JsonResponse(location_array,safe=False))


def get_methods_page(request):
    locations = core_models.Location.objects.all().order_by('location_id')

    location_array = []

    for x in locations:
        location_array.append(x.uuid)

    query_service_provided = core_models.CloseReferral.objects.filter(location_id__in=location_array
                                                                      ).values('service_provided').annotate(
        value=Count('service_provided'))

    methods_disaggregated = []

    for x in query_service_provided:

        query_selected_method = core_models.CloseReferral.objects.filter(location_id__in=location_array)
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
            query_client = core_models.Clients.objects.get(base_entity_id=y.base_entity_id)
            client_birth_date = query_client.birth_date
            client_gender = query_client.gender
            difference = relativedelta(now, client_birth_date)
            age_in_years = difference.years

            if 10 <= age_in_years <= 14:
                if client_gender == 'Female':
                    total_female_10_14 += 1
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

        methods_disaggregated.append({"method": x['service_provided'], "total_female_10_14": total_female_10_14,
                                      "total_female_15_19": total_female_15_19, "total_female_20_24": total_female_20_24,
                                      "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                      "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                      "total_male_25_": total_male_25_})

    return render(request, 'UserManagement/Features/Methods.html',{
        'methods_disaggregated':methods_disaggregated
    })


def get_household_page(request):
    locations = core_models.Location.objects.all().order_by('location_id')

    location_array = []

    for x in locations:
        location_array.append(x.uuid)

    household_themes = core_models.HouseholdThemes.objects.filter(location_id__in=location_array)

    total_female_10_14 = 0
    total_female_15_19 = 0
    total_female_20_24 = 0
    total_female_25_ = 0

    total_male_10_14 = 0
    total_male_15_19 = 0
    total_male_20_24 = 0
    total_male_25_ = 0

    household_array = []

    for y in household_themes:
        query_clients = core_models.Clients.objects.filter(client_id=y.client_id)

        for x in query_clients:
            now = datetime.now()

            client_birth_date = x.birth_date
            client_gender = x.gender
            difference = relativedelta(now, client_birth_date)
            age_in_years = difference.years

            if 10 <= age_in_years <= 14:
                if client_gender == 'Female':
                    total_female_10_14 += 1
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


    household_array.append({"total_female_10_14": total_female_10_14,
                            "total_female_15_19": total_female_15_19,
                            "total_female_20_24": total_female_20_24,
                            "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                            "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                            "total_male_25_": total_male_25_})

    return render(request, 'UserManagement/Features/HouseholdThemes.html',{
        'household_array':household_array
    })


def get_filtered_methods_page(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)

        query_service_provided = core_models.CloseReferral.objects.filter(event_date__gte=date_from,
                                                                          event_date__lte=date_to,
                                                                          location_id__in=children
                                                                          ).values('service_provided').annotate(
            value=Count('service_provided'))

        methods_disaggregated = []

        for x in query_service_provided:

            query_selected_method = core_models.CloseReferral.objects.filter(location_id__in=children)
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
                query_client = core_models.Clients.objects.get(base_entity_id=y.base_entity_id)
                client_birth_date = query_client.birth_date
                client_gender = query_client.gender
                difference = relativedelta(now, client_birth_date)
                age_in_years = difference.years

                if 10 <= age_in_years <= 14:
                    if client_gender == 'Female':
                        total_female_10_14 += 1
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

            methods_disaggregated.append({"method": x['service_provided'], "total_female_10_14": total_female_10_14,
                                          "total_female_15_19": total_female_15_19, "total_female_20_24": total_female_20_24,
                                          "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                          "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                          "total_male_25_": total_male_25_})

        return HttpResponse(JsonResponse(methods_disaggregated, safe=False))


def get_chw_performance_report(request):
    location_array = []
    locations = core_views.get_children_by_user(request.user)

    for x in locations:
        location_array.append(x.uuid)

    chw_array = []

    client_registration_by_chw = core_models.Clients.objects.filter(location_id__in=location_array
                                                                    ).values('provider_id').annotate(value=Count('provider_id')) \
                                     .order_by('-value')[: 10]

    for client in client_registration_by_chw:
        chw_id = client['provider_id']
        try:
            instance_team_member = core_models.TeamMembers.objects.get(identifier=chw_id)
            chw_name = instance_team_member.name
        except:
            chw_name = 'NIL'
        chw_object = {"chw_name": chw_name, "chw_id": chw_id,
                      "value": client['value']}

        chw_array.append(chw_object)

    referral_issued_by_chw = core_models.ReferralTask.objects.filter(
        health_facility_location_id__in=location_array). \
        values('chw_id', 'chw_name').annotate(value=Count('chw_id'))

    json_array_chw = []

    for x in referral_issued_by_chw:
        query_completed_referrals = core_models.ReferralTask.objects.filter(
            health_facility_location_id__in=location_array
            , chw_id=x['chw_id'], businessstatus='Complete')
        referral_object = {'chw_id': x['chw_id'], 'chw_name': x['chw_name'], 'issued': x['value'],
                           'completed': query_completed_referrals.count()}

        json_array_chw.append(referral_object)


    return render(request, 'UserManagement/Features/ChwPerformance.html',{
        'chw_array':chw_array,
        'referral_issued_by_chw': json_array_chw
    })


def get_filtered_chw_performance_report(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)

        chw_array = []
        json_array_chw = []

        client_registration_by_chw = core_models.Clients.objects.filter(location_id__in=children,
                                                                        event_date__gte=date_from,
                                                                        event_date__lte=date_to

                                                                        ).values('provider_id').annotate(value=Count('provider_id')) \
            .order_by('-value')

        referral_issued_by_chw = core_models.ReferralTask.objects.filter(
            health_facility_location_id__in=children, execution_start_date__gte=date_from,
            execution_start_date__lte=date_to
        ). \
            values('chw_id', 'chw_name').annotate(value=Count('chw_id'))

        for client in client_registration_by_chw:
            chw_id = client['provider_id']
            try:
                instance_team_member = core_models.TeamMembers.objects.get(identifier=chw_id)
                chw_name = instance_team_member.name
            except:
                chw_name = 'NIL'
            chw_object = {"chw_name": chw_name, "chw_id": chw_id,
                          "value": client['value']}

            chw_array.append(chw_object)

        for x in referral_issued_by_chw:
            query_completed_referrals = core_models.ReferralTask.objects.filter(
                health_facility_location_id__in=children, execution_start_date__gte=date_from,
                execution_start_date__lte=date_to

                , chw_id=x['chw_id'], businessstatus='Complete')
            referral_object = {'chw_id': x['chw_id'], 'chw_name': x['chw_name'], 'issued': x['value'],
                               'completed': query_completed_referrals.count()}

            json_array_chw.append(referral_object)

        content = {"chw_array":chw_array, "json_array_chw":json_array_chw}

        return HttpResponse(JsonResponse(content, safe=False))


def get_health_education_report(request):
    locations = core_models.Location.objects.all().order_by('location_id')

    location_array = []
    client_array = []

    for x in locations:
        location_array.append(x.uuid)

    query_fp_introduction = core_models.FamilyPlanningServices.objects.filter(location_id__in=location_array,
                                                                              event_type='Introduction to Family Planning')

    for y in query_fp_introduction:
        client_array.append(y.client_id)

    query_clients = core_models.Clients.objects.filter(client_id__in=client_array)

    fp_introduction_disaggregated = []

    total_female_10_14 = 0
    total_female_15_19 = 0
    total_female_20_24 = 0
    total_female_25_ = 0

    total_male_10_14 = 0
    total_male_15_19 = 0
    total_male_20_24 = 0
    total_male_25_ = 0

    for x in query_clients:
        now = datetime.now()

        client_birth_date = x.birth_date
        client_gender = x.gender
        difference = relativedelta(now, client_birth_date)
        age_in_years = difference.years

        if 10 <= age_in_years <= 14:
            if client_gender == 'Female':
                total_female_10_14 += 1
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

    fp_introduction_disaggregated.append({"total_female_10_14": total_female_10_14,
                                          "total_female_15_19": total_female_15_19,
                                          "total_female_20_24": total_female_20_24,
                                          "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                          "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                          "total_male_25_": total_male_25_})

    return render(request, 'UserManagement/Features/HealthEducation.html', {
        'fp_introduction_disaggregated':
            fp_introduction_disaggregated
    })


def get_filtered_health_education_report(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)

        location_array = []
        client_array = []

        query_fp_introduction = core_models.FamilyPlanningServices.objects.filter(location_id__in=children,
                                                                                  event_date__gte=date_from,
                                                                                  event_date__lte=date_to,
                                                                                  event_type='Introduction to Family Planning')

        for y in query_fp_introduction:
            client_array.append(y.client_id)

        query_clients = core_models.Clients.objects.filter(client_id__in=client_array)

        fp_introduction_disaggregated = []

        total_female_10_14 = 0
        total_female_15_19 = 0
        total_female_20_24 = 0
        total_female_25_ = 0

        total_male_10_14 = 0
        total_male_15_19 = 0
        total_male_20_24 = 0
        total_male_25_ = 0

        for x in query_clients:
            now = datetime.now()

            client_birth_date = x.birth_date
            client_gender = x.gender
            difference = relativedelta(now, client_birth_date)
            age_in_years = difference.years

            if 10 <= age_in_years <= 14:
                if client_gender == 'Female':
                    total_female_10_14 += 1
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

        fp_introduction_disaggregated.append({"total_female_10_14": total_female_10_14,
                                              "total_female_15_19": total_female_15_19,
                                              "total_female_20_24": total_female_20_24,
                                              "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                              "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                              "total_male_25_": total_male_25_})

        return HttpResponse(JsonResponse(fp_introduction_disaggregated, safe=False))


def get_client_summary(request):
    locations = core_models.Location.objects.all().order_by('location_id')
    location_array = []

    for x in locations:
        location_array.append(x.uuid)

    query_clients = core_models.Clients.objects.filter(location_id__in=location_array)
    clients_disaggregated = []

    total_female_10_14 = 0
    total_female_15_19 = 0
    total_female_20_24 = 0
    total_female_25_ = 0

    total_male_10_14 = 0
    total_male_15_19 = 0
    total_male_20_24 = 0
    total_male_25_ = 0

    for x in query_clients:
        now = datetime.now()

        client_birth_date = x.birth_date
        client_gender = x.gender

        difference = relativedelta(now, client_birth_date)
        age_in_years = difference.years

        if 10 <= age_in_years <= 14:
            if client_gender == 'Female':
                total_female_10_14 += 1
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

    total_male = total_male_10_14 + total_male_15_19 + total_male_20_24 + total_male_25_
    total_female = total_female_10_14 + total_female_15_19 + total_female_20_24 + total_female_25_
    total = total_female + total_male

    clients = core_models.Clients.objects.all()
    clients_table = ClientsTable(clients)
    RequestConfig(request, paginate={"per_page": 10}).configure(clients_table)

    clients_disaggregated.append({"total_female_10_14": total_female_10_14,
                                  "total_female_15_19": total_female_15_19,
                                  "total_female_20_24": total_female_20_24,
                                  "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                  "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                  "total_male_25_": total_male_25_
                                  })


    return render(request, 'UserManagement/Summary/Clients.html',{
        'clients':clients,
        'clients_disaggregated': clients_disaggregated,
        "total_male": total_male,
        "total_female": total_female,
        "total": total, "clients_table": clients_table
    })


def export_clients_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="clients.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['First name', 'Middle name', 'Last Name','Gender', 'Birth Date', 'Phone Number' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = core_models.Clients.objects.all().values_list('first_name', 'middle_name', 'last_name', 'gender', 'birth_date', 'phone_number')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def get_filtered_client_summary(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)

        query_clients = core_models.Clients.objects.filter(location_id__in=children,
                                                           event_date__gte=date_from, event_date__lte=date_to)

        total_female_10_14 = 0
        total_female_15_19 = 0
        total_female_20_24 = 0
        total_female_25_ = 0

        total_male_10_14 = 0
        total_male_15_19 = 0
        total_male_20_24 = 0
        total_male_25_ = 0

        for x in query_clients:
            now = datetime.now()

            client_birth_date = x.birth_date
            client_gender = x.gender

            difference = relativedelta(now, client_birth_date)
            age_in_years = difference.years

            if 10 <= age_in_years <= 14:
                if client_gender == 'Female':
                    total_female_10_14 += 1
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


        content =  {'total_female_10_14': total_female_10_14,
                    'total_female_15_19': total_female_15_19,
                    'total_female_20_24': total_female_20_24,
                    'total_female_25': total_female_25_,
                    'total_male_10_14': total_male_10_14,
                    'total_male_15_19': total_male_15_19,
                    'total_male_20_24': total_male_20_24,
                    'total_male_25': total_male_25_
                    }

        return HttpResponse(JsonResponse(content))


def get_referrals_summary(request):
    locations = core_models.Location.objects.all().order_by('location_id')
    location_array = []

    for x in locations:
        location_array.append(x.uuid)

    referral_status = core_models.ReferralTask.objects.filter(
        health_facility_location_id__in=location_array). \
        values('businessstatus').annotate(value=Count('businessstatus'))

    referral_types_focus = core_models.ReferralTask.objects.filter(
        health_facility_location_id__in=location_array). \
        values('focus').annotate(value=Count('focus'))

    # Fetch referrals by chw
    referral_issued_by_chw = core_models.ReferralTask.objects.filter(
        health_facility_location_id__in=location_array). \
        values('chw_id', 'chw_name').annotate(value=Count('chw_id'))

    json_array_chw = []
    json_array_total = []

    for x in referral_issued_by_chw:
        query_completed_referrals = core_models.ReferralTask.objects.filter(
            health_facility_location_id__in=location_array
            , chw_id=x['chw_id'], businessstatus='Complete')
        referral_object = {'chw_id': x['chw_id'], 'chw_name': x['chw_name'], 'issued': x['value'],
                           'completed': query_completed_referrals.count()}

        json_array_chw.append(referral_object)

    # Fetch referrals by type
    referral_total = core_models.ReferralTask.objects.filter(
        health_facility_location_id__in=location_array). \
        values('focus').annotate(value=Count('focus'))

    total_issued_referrals = core_models.Event.objects.filter(location_id__in=location_array). \
        filter(Q(event_type='ANC Referral') | Q(event_type='Family Planning Referral')
               | Q(event_type='Family Planning Referral Followup')).values('event_type'). \
        annotate(value=Count('event_type'))

    for y in referral_total:
        query_completed_referrals = core_models.ReferralTask.objects.filter(
            health_facility_location_id__in=location_array,
            businessstatus='Complete',
            focus=y['focus'])

        referral_object = {'focus': y['focus'], 'issued': y['value'],
                           'completed': query_completed_referrals.count()}

        json_array_total.append(referral_object)


    return render(request, 'UserManagement/Summary/Referrals.html', {'referral_types_focus': referral_types_focus,
                                                                     'referral_status': referral_status,
                                                                     'referral_issued_by_chw': json_array_chw,
                                                                     'referral_issued_total': json_array_total,
                                                                     'total_issued_referrals': total_issued_referrals
                                                                     })


def get_filtered_referrals_summary(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)

        referral_status = core_models.ReferralTask.objects.filter(execution_start_date__gte=date_from,
                                                                  execution_start_date__lte=date_to,
                                                                  health_facility_location_id__in=children). \
            values('businessstatus').annotate(value=Count('businessstatus'))

        referral_types_focus = core_models.ReferralTask.objects.filter(execution_start_date__gte=date_from,
                                                                       execution_start_date__lte=date_to,
                                                                       health_facility_location_id__in=children). \
            values('focus').annotate(value=Count('focus'))

        # Fetch referrals by chw
        referral_issued_by_chw = core_models.ReferralTask.objects.filter(execution_start_date__gte=date_from,
                                                                         execution_start_date__lte=date_to,
                                                                         health_facility_location_id__in=children). \
            values('chw_id', 'chw_name').annotate(value=Count('chw_id'))

        json_array_chw = []
        json_array_total = []

        for x in referral_issued_by_chw:
            query_completed_referrals = core_models.ReferralTask.objects.filter(
                execution_start_date__gte=date_from,
                execution_start_date__lte=date_to,
                health_facility_location_id__in=children
                , chw_id=x['chw_id'], businessstatus='Complete')
            referral_object = {'chw_id': x['chw_id'], 'chw_name': x['chw_name'], 'issued': x['value'],
                               'completed': query_completed_referrals.count()}

            json_array_chw.append(referral_object)

        # Fetch referrals by type
        referral_total = core_models.ReferralTask.objects.filter(
            health_facility_location_id__in=children). \
            values('focus').annotate(value=Count('focus'))

        total_issued_referrals = core_models.Event.objects.filter(event_date__gte=date_from,
                                                                  event_date__lte=date_to,
                                                                  location_id__in=children). \
            filter(Q(event_type='ANC Referral') | Q(event_type='Family Planning Referral')
                   | Q(event_type='Family Planning Referral Followup')).values('event_type'). \
            annotate(value=Count('event_type'))

        for y in referral_total:
            query_completed_referrals = core_models.ReferralTask.objects.filter(execution_start_date__gte=date_from,
                                                                                execution_start_date__lte=date_to,
                                                                                health_facility_location_id__in=children,
                                                                                businessstatus='Complete',
                                                                                focus=y['focus'])

            referral_object = {'focus': y['focus'], 'issued': y['value'],
                               'completed': query_completed_referrals.count()}

            json_array_total.append(referral_object)

        content = {'referral_types_focus': list(referral_types_focus),
                   'referral_status': list(referral_status),
                   'referral_issued_by_chw': json_array_chw,
                   'referral_issued_total': json_array_total,
                   'total_issued_referrals': list(total_issued_referrals)
                   }

        return HttpResponse(JsonResponse(content, safe=False))


def get_visit_summary(request):
    location_array = []
    locations = core_views.get_children_by_user(request)

    for x in locations:
        location_array.append(x.uuid)

    query_followups = core_models.Event.objects.filter(location_id__in=location_array
                                                       ).filter(Q(event_type='Fp Follow Up Visit') |
                                                                Q(event_type='Family Planning Method Referral Followup') |
                                                                Q(event_type='Family Planning Pregnancy Test Referral Followup') |
                                                                Q(event_type='Family Planning Method Refill Referral Followup')). \
        values('event_type').annotate(
        value=Count('event_type'))

    return render(request, 'UserManagement/Summary/Visits.html',{'query_followups':query_followups})


def filter_visit_summary(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)

        query_followups = core_models.Event.objects.filter(location_id__in=children, event_date__gte=date_from,
                                                           event_date__lte=date_to
                                                           ).filter(Q(event_type='Fp Follow Up Visit') |
                                                                    Q(event_type='Family Planning Method Referral Followup') |
                                                                    Q(event_type='Family Planning Pregnancy Test Referral Followup') |
                                                                    Q(event_type='Family Planning Method Refill Referral Followup')). \
            values('event_type').annotate(
            value=Count('event_type'))

        query_followups_json = list(query_followups)

        return HttpResponse(JsonResponse(query_followups_json, safe=False))


def get_initiations_summary(request):
    locations = core_models.Location.objects.all().order_by('location_id')

    location_array = []
    client_array = []

    for x in locations:
        location_array.append(x.uuid)

    query_fp_registrations = core_models.FamilyPlanningServices.objects.filter(location_id__in=location_array,
                                                                               event_type='Family Planning Registration')

    for y in query_fp_registrations:
        client_array.append(y.client_id)

    query_clients = core_models.Clients.objects.filter(client_id__in=client_array)

    fp_registrations_disaggregated = []

    total_female_10_14 = 0
    total_female_15_19 = 0
    total_female_20_24 = 0
    total_female_25_ = 0

    total_male_10_14 = 0
    total_male_15_19 = 0
    total_male_20_24 = 0
    total_male_25_ = 0

    for x in query_clients:
        now = datetime.now()

        client_birth_date = x.birth_date
        client_gender = x.gender
        difference = relativedelta(now, client_birth_date)
        age_in_years = difference.years

        if 10 <= age_in_years <= 14:
            if client_gender == 'Female':
                total_female_10_14 += 1
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

    fp_registrations_disaggregated.append({"total_female_10_14": total_female_10_14,
                                           "total_female_15_19": total_female_15_19,
                                           "total_female_20_24": total_female_20_24,
                                           "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                           "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                           "total_male_25_": total_male_25_})

    return render(request, 'UserManagement/Summary/Initiations.html', {
        'fp_registrations_disaggregated':
            fp_registrations_disaggregated
    })


def filter_initiations_summary(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)
        client_array = []


        query_fp_registrations = core_models.FamilyPlanningServices.objects.filter(location_id__in=children,
                                                                                   event_date__gte=date_from,
                                                                                   event_date__lte=date_to,
                                                                                   event_type='Family Planning Registration')

        for y in query_fp_registrations:
            client_array.append(y.client_id)

        query_clients = core_models.Clients.objects.filter(client_id__in=client_array)

        fp_registrations_disaggregated = []

        total_female_10_14 = 0
        total_female_15_19 = 0
        total_female_20_24 = 0
        total_female_25_ = 0

        total_male_10_14 = 0
        total_male_15_19 = 0
        total_male_20_24 = 0
        total_male_25_ = 0

        for x in query_clients:
            now = datetime.now()

            client_birth_date = x.birth_date
            client_gender = x.gender
            difference = relativedelta(now, client_birth_date)
            age_in_years = difference.years

            if 10 <= age_in_years <= 14:
                if client_gender == 'Female':
                    total_female_10_14 += 1
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

        fp_registrations_disaggregated.append({"total_female_10_14": total_female_10_14,
                                               "total_female_15_19": total_female_15_19,
                                               "total_female_20_24": total_female_20_24,
                                               "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                               "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                               "total_male_25_": total_male_25_})

        return render(request, 'UserManagement/Summary/Initiations.html', {
            'fp_registrations_disaggregated':
                fp_registrations_disaggregated
        })


def get_discontinuations_summary(request):
    location_array = []
    locations = core_views.get_children_by_user(request)

    for x in locations:
        location_array.append(x.uuid)

    total_family_planning_discontinuations = core_models.Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                              location_id__in=location_array).values('event_type').annotate(
        value=Count('event_type'))

    return render(request, 'UserManagement/Summary/Discontinuations.html', {'total_family_planning_discontinuations':total_family_planning_discontinuations})


def get_citizen_report_summary(request):
    location_array = []
    locations = core_views.get_children_by_user(request)

    for x in locations:
        location_array.append(x.uuid)

    query_wait_time = core_models.CitizenReportCard.objects.filter(location_id__in=location_array). \
        values('how_long_it_took_to_be_attended_by_service_provider').annotate \
        (value=Count('how_long_it_took_to_be_attended_by_service_provider'))


    query_attempts_complete = core_models.CitizenReportCard.objects.filter(location_id__in=location_array). \
        values('times_the_client_tried_to_complete_referral').annotate \
        (value=Count('times_the_client_tried_to_complete_referral'))

    query_reason_not_getting_service = core_models.CitizenReportCard.objects.filter(
        location_id__in=location_array). \
        values('reasons_for_not_getting_services').annotate \
        (value=Count('reasons_for_not_getting_services'))

    query_amount_asked_to_pay = core_models.CitizenReportCard.objects.filter(
        location_id__in=location_array). \
        values('amount_asked_to_pay_for_services').annotate \
        (value=Count('amount_asked_to_pay_for_services'))

    return render(request, 'UserManagement/Summary/CitizenReport.html', {'query_wait_time':query_wait_time,
                                                                         'query_attempts_complete':query_attempts_complete,
                                                                         'query_reason_not_getting_service':query_reason_not_getting_service,
                                                                         'query_amount_asked_to_pay':query_amount_asked_to_pay
                                                                         })


def filter_citizen_report_summary(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        children = core_views.get_facilities_by_location(parent_location_id)

        query_wait_time = core_models.CitizenReportCard.objects.filter(location_id__in=children,
                                                                       event_date__gte=date_from, event_date__lte=date_to). \
            values('how_long_it_took_to_be_attended_by_service_provider').annotate \
            (value=Count('how_long_it_took_to_be_attended_by_service_provider'))


        query_attempts_complete = core_models.CitizenReportCard.objects.filter(location_id__in=children,
                                                                               event_date__gte=date_from, event_date__lte=date_to). \
            values('times_the_client_tried_to_complete_referral').annotate \
            (value=Count('times_the_client_tried_to_complete_referral'))

        query_reason_not_getting_service = core_models.CitizenReportCard.objects.filter(
            location_id__in=children, event_date__gte=date_from, event_date__lte=date_to). \
            values('reasons_for_not_getting_services').annotate \
            (value=Count('reasons_for_not_getting_services'))

        query_amount_asked_to_pay = core_models.CitizenReportCard.objects.filter(
            location_id__in=children, event_date__gte=date_from, event_date__lte=date_to). \
            values('amount_asked_to_pay_for_services').annotate \
            (value=Count('amount_asked_to_pay_for_services'))

        content = {'query_wait_time': list(query_wait_time),
                   'query_attempts_complete': list(query_attempts_complete),
                   'query_reason_not_getting_service': list(query_reason_not_getting_service),
                   'query_amount_asked_to_pay': list(query_amount_asked_to_pay)
                   }

        return HttpResponse(JsonResponse(content, safe=False))


def authenticate_user(request):

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    if user is None:
        messages.success(request, 'Wrong credentials.')
        return render(request, 'UserManagement/Auth/Login.html')
    elif user.is_authenticated and user is not None:
        if user.is_superuser and user.is_active:
            login(request, user)
            return redirect('/admin/')
        elif user.is_active:
            login(request, user)
            date_from = date.today() - relativedelta(months=1)
            date_to = date.today() - relativedelta(days=1)

            location_array = []
            locations = core_views.get_children_by_user(user)

            for x in locations:
                location_array.append(x.uuid)

            content =  get_dashboard(request, date_from, date_to, location_array)

            return render(request, 'UserManagement/Dashboard/index.html', content)
        else:
            messages.success(request, 'Not allowed to access this portal')
            return render(request, 'UserManagement/Auth/Login.html')
    else:
        messages.success(request, 'Something went wrong, please try again later')
        return render(request, 'UserManagement/Auth/Login.html')



def get_dashboard(request, date_from, date_to, location_array):
    card_anc_referrals = core_models.Event.objects.filter(event_type='ANC Referral',event_date__gte=date_from,
                                                          event_date__lte=date_to,
                                                          location_id__in=location_array)
    card_family_planning_referrals = core_models.Event.objects.filter(event_type='Family Planning Referral',
                                                                      event_date__gte=date_from,
                                                                      event_date__lte=date_to,
                                                                      location_id__in=location_array)
    card_family_planning_initiations = core_models.Event.objects.filter(event_type='Family Planning Registration',
                                                                        event_date__gte=date_from,
                                                                        event_date__lte=date_to,
                                                                        location_id__in=location_array)
    card_family_planning_discontinuations = core_models.Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                             event_date__gte=date_from,
                                                                             event_date__lte=date_to,
                                                                             location_id__in=location_array)

    pop_given = core_models.GiveFpMethod.objects.filter(date_created__gte=date_from, date_created__lte=date_to,
                                                        pop_given='yes',
                                                        location_id__in=location_array
                                                        )

    coc_given = core_models.GiveFpMethod.objects.filter(date_created__gte=date_from, date_created__lte=date_to,
                                                        coc_given='yes',
                                                        location_id__in=location_array
                                                        )
    sdm_given = core_models.GiveFpMethod.objects.filter(date_created__gte=date_from, date_created__lte=date_to,
                                                        sdm_given='yes',
                                                        location_id__in=location_array
                                                        )

    male_condoms = core_models.GiveFpMethod.objects.filter(date_created__gte=date_from, date_created__lte=date_to,
                                                           male_condoms_given='yes',
                                                           location_id__in=location_array)

    content_methods = []
    content_clients = []

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
    content_methods.append({"method_type": "pop given", "items": total_pop_given})
    content_methods.append({"method_type": "coc given", "items": total_coc_given})
    content_methods.append({"method_type": "male condoms", "items": total_male_condoms})

    # total clients
    content_clients.append({"method_type": "pop given", "clients": pop_given.count()})
    content_clients.append({"method_type": "coc given", "clients": coc_given.count()})
    content_clients.append({"method_type": "male condoms", "clients": male_condoms.count()})

    content = {
        'card_anc_referrals': card_anc_referrals.count(),
        'card_family_planning_referrals':
            card_family_planning_referrals.count(),
        'card_family_planning_initiations':
            card_family_planning_initiations.count(),
        'card_family_planning_discontinuations':
            card_family_planning_discontinuations.count(),
        'total_fp_methods': content_methods,
        'total_clients': content_clients
    }

    return content


def filter_dashboard(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]
        parent_location_id = request.POST["location_id"]

        location_array = core_views.get_facilities_by_location(parent_location_id)

        content  = get_dashboard(request, date_from, date_to, location_array)

        return HttpResponse(JsonResponse(content, safe=False))
    else:
        date_from = date.today() - relativedelta(months=1)
        date_to = date.today() - relativedelta(days=1)

        location_array = []
        locations = core_views.get_children_by_user(request.user)

        for x in locations:
            location_array.append(x.uuid)

        content = get_dashboard(request, date_from, date_to, location_array)

        return render(request, 'UserManagement/Dashboard/index.html', content)



@login_required(login_url='/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(request.META['HTTP_REFERER'])

        else:
            messages.error(request, 'Please correct the error below.')
            return redirect(request.META['HTTP_REFERER'])
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'UserManagement/Auth/ChangePassword.html', {
            'form': form
        })

@login_required(login_url='/')
def logout(request):
    if request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


@login_required(login_url='/')
def set_changed_password(request):

    if request.POST:
        old_password = request.POST['old_password']
        new_password = request.POST['new_password2']

        user = authenticate(request, username=request.user.username, password=old_password)

        if user is not None and user.is_authenticated:
            logged_user = User.objects.get(username = request.user.username)
            logged_user.set_password(new_password)
            logged_user.save()

            return HttpResponse(status=200)

        else:

            return HttpResponse(status=401)