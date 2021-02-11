from django.shortcuts import render
from django.conf import settings
from django.db.models import Func, Q
from Core import models as core_models
import json


# Create your views here.):
def get_children_by_user(request):
    starting_location = core_models.Location.objects.get(location_id=request.user.profile.location.location_id)

    # Regions
    location_children = core_models.Location.objects.filter(parent_location=starting_location.id)

    if location_children.count() > 0:
        # Districts
        level_1 = core_models.Location.objects.filter(parent_location__in=location_children.values('location_id'))

        if level_1.count() > 0:
            # Wards
            level_2 = core_models.Location.objects.filter(parent_location__in=level_1.values('location_id'))

            if level_2.count() > 0:
                # Facilities
                level_3 = core_models.Location.objects.filter(parent_location__in=level_2.values('location_id'))
                if level_3.count() > 0:
                    # Villages
                    level_4 = core_models.Location.objects.filter(parent_location__in=level_3.values('location_id'))
                    if level_4.count() > 0:
                        children = level_4
                    else:
                        children = level_3
                else:
                    children = level_3
            else:
                children = level_2

        else:
            children = location_children
    else:
        # Work around to return a queryset so as to count()
        children = core_models.Location.objects.filter(id=request.user.profile.location.id)

    return children


def get_dashboard_summary(request):
    location_array = []
    locations = get_children_by_user(request)

    for x in locations:
        location_array.append(x.uuid)

    total_clients = core_models.Clients.objects.filter(location_id__in=location_array)
    total_clients_families = core_models.Household.objects.filter(location_id__in=location_array)
    total_referrals = core_models.ReferralTask.objects.filter(health_facility_location_id__in=location_array)
    total_family_planning_initiations = core_models.Event.objects.filter(event_type='Family Planning Registration',
                                                                         location_id__in=location_array)
    total_family_planning_discontinuations = core_models.Event.objects.filter(event_type='Family Planning Discontinuation',
                                                                              location_id__in=location_array)
    total_citizen_reports = core_models.Event.objects.filter(event_type='Citizen Report Card',
                                                             location_id__in=location_array)
    total_visits = core_models.Event.objects.filter(location_id__in=location_array).filter(Q(event_type='Fp Follow Up Visit') |
                                                                                           Q(
                                                                                               event_type='Family Planning Method Referral Followup') |
                                                                                           Q(
                                                                                               event_type='Family Planning Pregnancy Test Referral Followup')).values('event_type')
    content = {
        'total_clients': total_clients.count(),
        'total_visits': total_visits.count(),
        'total_referrals': total_referrals.count(),
        'total_family_planning_initiations': total_family_planning_initiations.count(),
        'total_family_planning_discontinuations': total_family_planning_discontinuations.count(),
        'total_clients_families': total_clients_families.count(),
        'total_citizen_reports': total_citizen_reports.count()
    }

    return content

# Logic to create dashboard tree
def get_children_recursively(parent_location_id):
    final_children = []

    all_locations = core_models.Location.objects.all()

    for x in all_locations:
        if x.parent_location == parent_location_id:
            # add this object to an array
            # children.append({"id": x.id, "text": ""+x.location_name+""})

            if len((get_children_recursively(x.location_id))) > 0:
                final_children.append(
                    {"id": x.location_id, "text": "" + x.name + "", "inc": (get_children_recursively(x.location_id))})
            else:
                final_children.append(
                    {"id": x.location_id, "text": "" + x.name + ""})

    return final_children

def get_parent_child_relationship(request):
    json_data = ""
    starting_location_id = request.user.profile.location.location_id
    exact_location = core_models.Location.objects.get(location_id=starting_location_id)
    parent_id = exact_location.parent_location
    if parent_id is None:
        parent_id = starting_location_id
    else:
        parent_id = exact_location.parent_location
    all_locations = core_models.Location.objects.all()
    for x in all_locations:
        if x.location_id == parent_id:
            children = get_children_recursively(parent_id)
            if len(children) > 0:
                json_data = [{"id": x.location_id, "text": x.name, "inc": children}]

            else:
                pass
    return json.dumps(json_data)