from django.conf import settings
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from Core import models as core_models
from Core import views as core_views
from .tables import TeamTable, LocationTable
from django.db.models import Count
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.http import HttpResponse
from django.http import JsonResponse


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
    content = core_views.get_dashboard_summary(request)
    locations = core_models.Location.objects.all().order_by('location_id')
    locations_table = LocationTable(locations)
    RequestConfig(request, paginate={"per_page": 10}).configure(locations_table)
    return render(request, 'UserManagement/Features/LocationManagement.html', {'locations_table':locations_table,
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


def get_team_management_page(request):
    content = core_views.get_dashboard_summary(request)
    teams = core_models.Team.objects.all().order_by('team_id')
    teams_table = TeamTable(teams)
    RequestConfig(request, paginate={"per_page": 10}).configure(teams_table)
    return render(request, 'UserManagement/Features/TeamManagement.html',{'teams_table':teams_table,
                                                                          'total_clients': content['total_clients'],
                                                                          'total_referrals': content['total_referrals'],
                                                                          'total_visits': content['total_visits'],
                                                                          'total_family_planning_initiations': content['total_family_planning_initiations'],
                                                                          'total_family_planning_discontinuations': content['total_family_planning_discontinuations'],
                                                                          'total_citizen_reports': content['total_citizen_reports']})


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


def get_chw_performance_report(request):
    content = core_views.get_dashboard_summary(request)
    location_array = []
    locations = core_views.get_children_by_user(request)

    for x in locations:
        location_array.append(x.uuid)

    chw_array = []

    client_registration_by_chw = core_models.Clients.objects.filter(location_id__in=location_array
                                                                    ).values('provider_id').annotate(value=Count('provider_id')) \
        .order_by('-value')

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

    return render(request, 'UserManagement/Features/ChwPerformance.html',{'total_clients': content['total_clients'],
                                                                          'total_referrals': content['total_referrals'],
                                                                          'total_visits': content['total_visits'],
                                                                          'total_family_planning_initiations': content[
                                                                              'total_family_planning_initiations'],
                                                                          'total_family_planning_discontinuations': content[
                                                                              'total_family_planning_discontinuations'],
                                                                          'total_citizen_reports': content[
                                                                              'total_citizen_reports'],
                                                                          'chw_array':chw_array
                                                                          })


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


def get_client_summary(request):
    content = core_views.get_dashboard_summary(request)
    clients = core_models.Client.objects.all()
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


    clients_disaggregated.append({"total_female_10_14": total_female_10_14,
                                  "total_female_15_19": total_female_15_19,
                                  "total_female_20_24": total_female_20_24,
                                  "total_female_25_": total_female_25_, "total_male_10_14": total_male_10_14,
                                  "total_male_15_19": total_male_15_19, "total_male_20_24": total_male_20_24,
                                  "total_male_25_": total_male_25_})


    return render(request, 'UserManagement/Summary/Clients.html',{'total_clients': content['total_clients'],
                                                                  'total_referrals': content['total_referrals'],
                                                                  'total_visits': content['total_visits'],
                                                                  'total_family_planning_initiations': content[
                                                                      'total_family_planning_initiations'],
                                                                  'total_family_planning_discontinuations': content[
                                                                      'total_family_planning_discontinuations'],
                                                                  'total_citizen_reports': content[
                                                                      'total_citizen_reports'],
                                                                  'clients':clients,
                                                                  'clients_disaggregated': clients_disaggregated
                                                                  })


def get_filtered_client_summary(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]

        locations = core_models.Location.objects.all().order_by('location_id')
        location_array = []

        for x in locations:
            location_array.append(x.uuid)

        query_clients = core_models.Clients.objects.filter(location_id__in=location_array,
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
    # content = core_views.get_dashboard_summary(request)
    # {'total_clients': content['total_clients'],
    #  'total_referrals': content['total_referrals'],
    #  'total_visits': content['total_visits'],
    #  'total_family_planning_initiations': content[
    #      'total_family_planning_initiations'],
    #  'total_family_planning_discontinuations': content[
    #      'total_family_planning_discontinuations'],
    #  'total_citizen_reports': content[
    #      'total_citizen_reports']
    #  }
    return render(request, 'UserManagement/Summary/Referrals.html')


def get_visit_summary(request):
    content = core_views.get_dashboard_summary(request)
    return render(request, 'UserManagement/Summary/Visits.html', {'total_clients': content['total_clients'],
                                                                  'total_referrals': content['total_referrals'],
                                                                  'total_visits': content['total_visits'],
                                                                  'total_family_planning_initiations': content[
                                                                      'total_family_planning_initiations'],
                                                                  'total_family_planning_discontinuations': content[
                                                                      'total_family_planning_discontinuations'],
                                                                  'total_citizen_reports': content[
                                                                      'total_citizen_reports']
                                                                  })


def get_initiations_summary(request):
    content = core_views.get_dashboard_summary(request)
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

    return render(request, 'UserManagement/Summary/Initiations.html', {'total_clients': content['total_clients'],
                                                                       'total_referrals': content['total_referrals'],
                                                                       'total_visits': content['total_visits'],
                                                                       'total_family_planning_initiations': content[
                                                                           'total_family_planning_initiations'],
                                                                       'total_family_planning_discontinuations':
                                                                           content[
                                                                               'total_family_planning_discontinuations'],
                                                                       'total_citizen_reports': content[
                                                                           'total_citizen_reports'],
                                                                       'fp_registrations_disaggregated':
                                                                           fp_registrations_disaggregated
                                                                       })


def get_discontinuations_summary(request):
    content = core_views.get_dashboard_summary(request)
    return render(request, 'UserManagement/Summary/Discontinuations.html', {'total_clients': content['total_clients'],
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


def get_citizen_report_summary(request):
    content = core_views.get_dashboard_summary(request)
    return render(request, 'UserManagement/Summary/CitizenReport.html', {'total_clients': content['total_clients'],
                                                                         'total_referrals': content['total_referrals'],
                                                                         'total_visits': content['total_visits'],
                                                                         'total_family_planning_initiations': content[
                                                                             'total_family_planning_initiations'],
                                                                         'total_family_planning_discontinuations':
                                                                             content[
                                                                                 'total_family_planning_discontinuations'],
                                                                         'total_citizen_reports': content[
                                                                             'total_citizen_reports']
                                                                         })


def authenticate_user(request):

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)

    if user.is_authenticated:

        if user.is_active:
            if user.is_superuser:
                login(request, user)
                return redirect('/admin/')
            elif user.is_staff:
                return redirect('/dashboard')
            else:
                return render(request, 'UserManagement/Auth/Login.html')
        else:
            return render(request, 'UserManagement/Auth/Login.html')
    else:
        return render(request, 'UserManagement/Auth/Login.html')


def get_dashboard(request):
    content = core_views.get_dashboard_summary(request)
    # tree_locations = core_views.get_parent_child_relationship(request)

    location_array = []
    locations = core_views.get_children_by_user(request)

    for x in locations:
        location_array.append(x.uuid)

    card_anc_referrals = core_models.Event.objects.filter(event_type='ANC Referral',
                                                          location_id__in=location_array)

    card_family_planning_referrals = core_models.Event.objects.filter(event_type='Family Planning Referral',
                                                                      location_id__in=location_array)
    card_family_planning_initiations = core_models.Event.objects.filter(event_type='Family Planning Registration',
                                                                        location_id__in=location_array)
    card_family_planning_discontinuations = core_models.Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                             location_id__in=location_array)
    return render(request, 'UserManagement/Dashboard/index.html',{
        'total_clients': content['total_clients'],
        'total_referrals': content['total_referrals'],
        'total_visits': content['total_visits'],
        'total_family_planning_initiations': content[
            'total_family_planning_initiations'],
        'total_family_planning_discontinuations':
            content[
                'total_family_planning_discontinuations'],
        'total_citizen_reports': content[
            'total_citizen_reports'],
        'card_anc_referrals':card_anc_referrals.count(),
        'card_family_planning_referrals':
            card_family_planning_referrals.count(),
        'card_family_planning_initiations':
            card_family_planning_initiations.count(),
        'card_family_planning_discontinuations':
            card_family_planning_discontinuations.count(),
        # 'tree_locations': tree_locations

    })


def get_filtered_dashboard(request,date_from, date_to):
    content = core_views.get_dashboard_summary(request)
    # tree_locations = core_views.get_parent_child_relationship(request)

    location_array = []
    locations = core_views.get_children_by_user(request)

    for x in locations:
        location_array.append(x.uuid)

    card_anc_referrals = core_models.Event.objects.filter(event_type='ANC Referral',
                                                          location_id__in=location_array, event_date__gte=date_from,
                                                          event_date__lte=date_to)

    card_family_planning_referrals = core_models.Event.objects.filter(event_type='Family Planning Referral',
                                                                      location_id__in=location_array,
                                                                      event_date__gte=date_from,
                                                                      event_date__lte=date_to
                                                                      )
    card_family_planning_initiations = core_models.Event.objects.filter(event_type='Family Planning Registration',
                                                                        location_id__in=location_array,
                                                                        event_date__gte=date_from,
                                                                        event_date__lte=date_to
                                                                        )
    card_family_planning_discontinuations = core_models.Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                             location_id__in=location_array,
                                                                             event_date__gte=date_from,
                                                                             event_date__lte=date_to)
    content = {
        'card_anc_referrals': card_anc_referrals.count(),
        'card_family_planning_referrals':
            card_family_planning_referrals.count(),
        'card_family_planning_initiations':
            card_family_planning_initiations.count(),
        'card_family_planning_discontinuations':
            card_family_planning_discontinuations.count()}


    return JsonResponse(content)


def filter_dashboard(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]

        path = get_filtered_dashboard(request,date_from, date_to)

        return HttpResponse(path)


@login_required(login_url='/')
def logout(request):
    logout(request)
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))