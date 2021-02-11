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
    base_entity_id = models.CharField(max_length=255, null=True, blank=True)
    family = models.CharField(max_length=255, null=True, blank=True)


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

    client = models.CharField(max_length=255, null=True, blank=True)
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
    team = models.CharField(max_length=255, null=True, blank=True)
    team_id = models.CharField(max_length=255, null=True, blank=True)
    event_type = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    base_entity_id = models.CharField(max_length=255, null=True, blank=True)
    form_submission_id = models.CharField(max_length=255, null=True, blank=True)

    willing_to_participate_in_survey = models.CharField(max_length=255, null=True, blank=True)
    name_of_health_facility_visited_for_family_planning_services = models.CharField(max_length=255, null=True,                                                                                   blank=True)
    did_the_client_complete_referral = models.CharField(max_length=255, null=True, blank=True)
    times_the_client_tried_to_complete_referral = models.CharField(max_length=255, null=True, blank=True)
    how_long_it_took_to_be_attended_by_service_provider = models.CharField(max_length=255, null=True, blank=True)
    was_client_screened_for_pregnancy = models.CharField(max_length=255, null=True, blank=True)
    amount_asked_to_pay_for_services = models.CharField(max_length=255, null=True, blank=True)
    reasons_for_not_getting_services = models.CharField(max_length=255, null=True, blank=True)
    treatment_from_service_providers = models.CharField(max_length=255, null=True, blank=True)
    satisfied_with_fp_services_from_health_facility = models.CharField(max_length=255, null=True, blank=True)
    satisfied_with_fp_services_from_chw = models.CharField(max_length=255, null=True, blank=True)

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


class CloseReferral(models.Model):
    def __str__(self):
        return '%d' % self.id

    event_id = models.IntegerField(null=True, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    team = models.CharField(max_length=100, null=True, blank=True)
    team_id = models.CharField(max_length=100, null=True, blank=True)
    event_type = models.CharField(max_length=100, null=True, blank=True)
    location_id = models.CharField(max_length=100, null=True, blank=True)
    provider_id = models.CharField(max_length=100, null=True, blank=True)
    base_entity_id = models.CharField(max_length=100, null=True, blank=True)
    form_submission_id = models.CharField(max_length=100, null=True, blank=True)

    referral_task = models.CharField(max_length=100, null=True, blank=True)
    referral_task_previous_status = models.CharField(max_length=100, null=True, blank=True)
    referral_task_previous_business_status = models.CharField(max_length=255, null=True, blank=True)
    service_provided = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "close_referral"


class FamilyPlanningServices(models.Model):
    def __str__(self):
        return '%d' % self.id

    event_id = models.IntegerField(null=True, blank=True)
    client_id = models.BigIntegerField(null=True, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    team = models.CharField(max_length=100, null=True, blank=True)
    team_id = models.CharField(max_length=100, null=True, blank=True)
    event_type = models.CharField(max_length=100, null=True, blank=True)
    location_id = models.CharField(max_length=100, null=True, blank=True)
    provider_id = models.CharField(max_length=100, null=True, blank=True)
    base_entity_id = models.CharField(max_length=100, null=True, blank=True)


    class Meta:
        db_table = "family_planning_services"


class TeamMembers(models.Model):
    def __str__(self):
        return '%d' %self.id

    identifier = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    location_uuid = models.CharField(max_length=255, null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    team_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "team_members"


class Team(models.Model):
    def __str__(self):
        return '%d' % self.id

    team_id = models.IntegerField()
    identifier = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    location_id = models.IntegerField()
    uuid = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "teams"


class Location(models.Model):
    def __str__(self):
        return '%s' % self.name

    location_id = models.IntegerField()
    name = models. CharField(max_length=255)
    description = models. CharField(max_length=255, null=True, blank=True)
    address_1 = models. CharField(max_length=255, null=True, blank=True)
    address_2 = models. CharField(max_length=255, null=True, blank=True)
    address_3 = models.CharField(max_length=255, null=True, blank=True)
    city_village = models. IntegerField(null=True, blank=True)
    state_province = models. IntegerField(null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    county_district = models.CharField(max_length=255, null=True, blank=True)
    retired = models.IntegerField(null=True, blank=True)
    retire_reason = models.CharField(max_length=255, null=True, blank=True)
    parent_location = models.IntegerField(null=True, blank=True)
    uuid = models.CharField(max_length=255,null=True, blank=True)


    class Meta:
        db_table = "locations"