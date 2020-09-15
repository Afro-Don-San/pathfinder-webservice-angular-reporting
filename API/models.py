from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Client(models.Model):
    def __str__(self):
        return '%d' % self.id

    id = models.BigIntegerField(db_column="id", primary_key=True)
    client_id = models.CharField(db_column="client_id", max_length=255)
    base_entity_id = models.CharField(db_column="base_entity_id", max_length=255)
    relational_id = models.CharField(db_column="relational_id", max_length=255)
    server_version = models.CharField(db_column="server_version", max_length=255)
    openmrs_uuid = models.CharField(db_column="openmrs_uuid", max_length=255)
    unique_id = models.CharField(db_column="unique_id", max_length=255)
    first_name = models.CharField(db_column="first_name", max_length=255)
    middle_name = models.CharField(db_column="middle_name", max_length=255)
    last_name = models.CharField(db_column="last_name", max_length=255)
    birth_date = models.DateField(db_column="birth_date")
    date_deleted = models.DateTimeField(db_column="date_deleted")
    residence = models.CharField(db_column="residence", max_length=255)

    class Meta:
        managed = False
        db_table = 'client_metadata'


class Event(models.Model):
    def __str__(self):
        return '%d' % self.id

    id = models.BigIntegerField(db_column="id", primary_key=True)
    event_id = models.BigIntegerField(db_column="event_id")
    document_id = models.CharField(db_column="document_id", max_length=255)
    base_entity_id = models.CharField(db_column="base_entity_id", max_length=255)
    form_submission_id = models.CharField(db_column="form_submission_id", max_length=255)
    server_version = models.CharField(db_column="server_version", max_length=255)
    openmrs_uuid = models.CharField(db_column="openmrs_uuid", max_length=255)
    event_type = models.CharField(db_column="event_type", max_length=255)
    event_date = models.DateTimeField(db_column="event_date")
    entity_type = models.CharField(db_column="entity_type", max_length=255)
    provider_id = models.CharField(db_column="provider_id", max_length=255)
    location_id = models.CharField(db_column="location_id", max_length=255)
    team = models.CharField(db_column="team", max_length=255)
    team_id = models.CharField(db_column="team_id", max_length=255)
    date_created = models.DateTimeField(db_column="date_created")
    date_edited = models.DateTimeField(db_column="date_edited")
    date_deleted = models.DateTimeField(db_column="date_deleted")

    class Meta:
        managed = False
        db_table = 'event_metadata'


class Clients(models.Model):
    def __str__(self):
        return '%d' % self.id

    client_id = models.CharField(max_length=255, null=True, blank=True)
    event_id = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField( max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255,null=True, blank=True)
    client_type = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    team = models.CharField(max_length=255, null=True, blank=True)
    team_id = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    family_location_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'clients'


class Household(models.Model):
    def __str__(self):
        return '%d' % self.id

    client_id = models.CharField(max_length=255, null=True, blank=True)
    event_id = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField( max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255,null=True, blank=True)
    client_type = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.CharField(max_length=255, null=True, blank=True)
    team = models.CharField(max_length=255, null=True, blank=True)
    team_id = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    family_location_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'households'


class Referral(models.Model):
    def __str__(self):
        return '%d' % self.id

    event_id = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.CharField(max_length=255, null=True, blank=True)
    event_type = models.CharField(max_length=255, null=True, blank=True)
    team = models.CharField(max_length=255, null=True, blank=True)
    team_id = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    referral_status = models.CharField(max_length=255, null=True, blank=True)
    chw_referral_service = models.CharField(max_length=255, null=True, blank=True)
    referral_date = models.CharField(max_length=255, null=True, blank=True)
    referral_type = models.CharField(max_length=255, null=True, blank=True)
    referral_appointment_date = models.CharField(max_length=255, null=True, blank=True)
    referral_time = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        db_table = 'referrals'


class ReferralTask(models.Model):
    def __str__(self):
        return '%d' % self.id

    task_id = models.CharField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    execution_start_date = models.DateField(null=True, blank=True)
    referred_client_base_entity_id = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    focus = models.CharField(max_length=255, null=True, blank=True)
    chw_id = models.CharField(max_length=255, null=True, blank=True)
    health_facility_location_id = models.CharField(max_length=255, null=True, blank=True)
    chw_name = models.CharField(max_length=255, null=True, blank=True)
    businessstatus = models.CharField(max_length=255, null=True, blank=True)
    referral_formsubmissionid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'referral_tasks'


class CitizenReportCard(models.Model):
    def __str__(self):
        return '%d' % self.id

    event_id = models.IntegerField(null=True, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    willing_to_participate_in_survey = models.CharField(max_length=255, null=True, blank=True)
    name_of_health_facility_visited_for_family_planning_services = models.CharField(max_length=255, null=True, blank=True)
    residence = models.CharField(max_length=255, null=True, blank=True)
    education = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(max_length=255, null=True, blank=True)
    religion = models.CharField(max_length=255, null=True, blank=True)
    reasons_for_people_not_going_to_health_facilities = models.CharField(max_length=255, null=True, blank=True)
    means_of_transport_to_facility = models.CharField(max_length=255, null=True, blank=True)
    time_to_reach_facility_closest_from_household = models.CharField(max_length=255, null=True, blank=True)
    is_this_the_nearest_facility_from_home = models.CharField(max_length=255, null=True, blank=True)
    was_the_facility_open_when_you_arrived = models.CharField(max_length=255, null=True, blank=True)
    did_you_arrive_during_normal_operating_hours = models.CharField(max_length=255, null=True, blank=True)
    did_you_get_family_planning_information_at_the_reception = models.CharField(max_length=255, null=True, blank=True)
    how_long_it_took_to_be_attended_by_service_provider = models.CharField(max_length=255, null=True, blank=True)
    did_the_service_provider_make_you_feel_welcome = models.CharField(max_length=255, null=True, blank=True)
    did_the_service_provider_assure_confidentiality = models.CharField(max_length=255, null=True, blank=True)
    did_you_meet_the_service_providers_in_a_private_room = models.CharField(max_length=255, null=True, blank=True)
    did_the_providers_give_clear_info_about_services_and_methods = models.CharField(max_length=255, null=True, blank=True)
    did_the_service_providers_use_visual_aids_to_demo_fp_methods = models.CharField(max_length=255, null=True, blank=True)
    did_the_providers_ask_of_any_concerns_about_used_methods = models.CharField(max_length=255, null=True, blank=True)
    were_you_given_info_on_dual_protection = models.CharField(max_length=255, null=True, blank=True)
    visited_facility_for_fp_services_but_not_get_services_needed = models.CharField(max_length=255, null=True, blank=True)
    why_did_you_not_get_the_services_at_the_health_facility = models.CharField(max_length=255, null=True, blank=True)
    did_you_pay_for_the_service = models.CharField(max_length=255, null=True, blank=True)
    were_you_asked_to_give_some_kickbacks_to_get_the_service = models.CharField(max_length=255, null=True, blank=True)
    did_you_file_a_complaint = models.CharField(max_length=255, null=True, blank=True)
    was_your_problem_solved_to_satisfaction = models.CharField(max_length=255, null=True, blank=True)
    did_you_report_the_problem_again = models.CharField(max_length=255, null=True, blank=True)
    will_you_go_back_for_fp_services_at_this_facility = models.CharField(max_length=255, null=True, blank=True)
    are_you_satisfied_with_fp_services_you_received = models.CharField(max_length=255, null=True, blank=True)
    are_you_satisfied_with_fp_services_provided_using_phone = models.CharField(max_length=255, null=True, blank=True)
    have_fp_services_improved = models.CharField(max_length=255, null=True, blank=True)
    team = models.CharField(max_length=255, null=True, blank=True)
    team_id = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        db_table = 'citizen_report_cards'


class GiveFpMethod(models.Model):
    def __str__(self):
        return '%d' % self.id

    event_id = models.IntegerField(null=True, blank=True),
    give_fp_method_done = models.CharField(max_length=100, null=True, blank=True)
    fp_method_given = models.CharField(max_length=100, null=True, blank=True)
    male_condoms_given = models.CharField(max_length=100, null=True, blank=True)
    number_of_condoms = models.IntegerField(null=True, blank=True)
    coc_given = models.CharField(max_length=100, null=True, blank=True)
    pop_given = models.CharField(max_length=100, null=True, blank=True)
    sdm_given = models.CharField(max_length=100, null=True, blank=True)
    number_of_pills = models.IntegerField(null=True, blank=True)
    team = models.CharField(max_length=100, null=True, blank=True)
    team_id = models.CharField(max_length=100, null=True, blank=True)
    event_type = models.CharField(max_length=100, null=True, blank=True)
    location_id = models.CharField(max_length=100, null=True, blank=True)
    provider_id = models.CharField(max_length=100, null=True, blank=True)
    base_entity_id = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateField(null=True, blank=True)
    form_submission_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "give_family_planning_methods"


