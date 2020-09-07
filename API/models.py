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


class ClientExtended(models.Model):
    def __str__(self):
        return '%d' % self.id

    Female = 'Female'
    Male = 'Male'

    GENDER_TYPE_CHOICES = (
        (Female, 'Female'),
        (Male, 'Male')
    )

    date_time_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_TYPE_CHOICES)

    class Meta:
        db_table = 'clients_extended'


class EventExtended(models.Model):

    event_id = models.CharField(max_length=255, null=True, blank=True)
    event_type = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)
    entity_type = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    team = models.CharField(max_length=255, null=True, blank=True)
    team_id = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.CharField(max_length=255, null=True, blank=True)

    values_0 = models.CharField(max_length=255, null=True, blank=True)
    field_code_0 = models.CharField(max_length=255, null=True, blank=True)
    field_type_0 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_0_0 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_0 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_0 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_0 = models.CharField(max_length=255, null=True, blank=True)

    values_1 = models.CharField(max_length=255, null=True, blank=True)
    field_code_1 = models.CharField(max_length=255, null=True, blank=True)
    field_type_1 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_1 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_1 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_1 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_1 = models.CharField(max_length=255, null=True, blank=True)

    values_2 = models.CharField(max_length=255, null=True, blank=True)
    field_code_2 = models.CharField(max_length=255, null=True, blank=True)
    field_type_2 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_2 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_2 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_2 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_2 = models.CharField(max_length=255, null=True, blank=True)

    values_3 = models.CharField(max_length=255, null=True, blank=True)
    field_code_3 = models.CharField(max_length=255, null=True, blank=True)
    field_type_3 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_3 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_3 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_3 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_3 = models.CharField(max_length=255, null=True, blank=True)

    values_4 = models.CharField(max_length=255, null=True, blank=True)
    field_code_4 = models.CharField(max_length=255, null=True, blank=True)
    field_type_4 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_4 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_4 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_4 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_4 = models.CharField(max_length=255, null=True, blank=True)

    values_5 = models.CharField(max_length=255, null=True, blank=True)
    field_code_5 = models.CharField(max_length=255, null=True, blank=True)
    field_type_5 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_5 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_5 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_5 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_5 = models.CharField(max_length=255, null=True, blank=True)

    values_6 = models.CharField(max_length=255, null=True, blank=True)
    field_code_6 = models.CharField(max_length=255, null=True, blank=True)
    field_type_6 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_6 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_6 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_6 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_6 = models.CharField(max_length=255, null=True, blank=True)

    values_7 = models.CharField(max_length=255, null=True, blank=True)
    field_code_7 = models.CharField(max_length=255, null=True, blank=True)
    field_type_7 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_7 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_7 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_7 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_7 = models.CharField(max_length=255, null=True, blank=True)

    values_8 = models.CharField(max_length=255, null=True, blank=True)
    field_code_8 = models.CharField(max_length=255, null=True, blank=True)
    field_type_8 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_8 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_8 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_8 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_8 = models.CharField(max_length=255, null=True, blank=True)

    values_9 = models.CharField(max_length=255, null=True, blank=True)
    field_code_9 = models.CharField(max_length=255, null=True, blank=True)
    field_type_9 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_9 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_9 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_9 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_9 = models.CharField(max_length=255, null=True, blank=True)

    values_10 = models.CharField(max_length=255, null=True, blank=True)
    field_code_10 = models.CharField(max_length=255, null=True, blank=True)
    field_type_10 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_10 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_10 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_10 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_10 = models.CharField(max_length=255, null=True, blank=True)

    values_11 = models.CharField(max_length=255, null=True, blank=True)
    field_code_11 = models.CharField(max_length=255, null=True, blank=True)
    field_type_11 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_11 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_11 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_11 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_11 = models.CharField(max_length=255, null=True, blank=True)

    values_12 = models.CharField(max_length=255, null=True, blank=True)
    field_code_12 = models.CharField(max_length=255, null=True, blank=True)
    field_type_12 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_12 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_12 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_12 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_12 = models.CharField(max_length=255, null=True, blank=True)

    values_13 = models.CharField(max_length=255, null=True, blank=True)
    field_code_13 = models.CharField(max_length=255, null=True, blank=True)
    field_type_13 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_13 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_13 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_13 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_13 = models.CharField(max_length=255, null=True, blank=True)

    values_14 = models.CharField(max_length=255, null=True, blank=True)
    field_code_14 = models.CharField(max_length=255, null=True, blank=True)
    field_type_14 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_14 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_14 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_14 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_14 = models.CharField(max_length=255, null=True, blank=True)

    values_15 = models.CharField(max_length=255, null=True, blank=True)
    field_code_15 = models.CharField(max_length=255, null=True, blank=True)
    field_type_15 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_15 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_15 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_15 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_15 = models.CharField(max_length=255, null=True, blank=True)

    values_16 = models.CharField(max_length=255, null=True, blank=True)
    field_code_16 = models.CharField(max_length=255, null=True, blank=True)
    field_type_16 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_16 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_16 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_16 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_16 = models.CharField(max_length=255, null=True, blank=True)

    values_17 = models.CharField(max_length=255, null=True, blank=True)
    field_code_17 = models.CharField(max_length=255, null=True, blank=True)
    field_type_17 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_17 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_17 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_17 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_17 = models.CharField(max_length=255, null=True, blank=True)

    values_18 = models.CharField(max_length=255, null=True, blank=True)
    field_code_18 = models.CharField(max_length=255, null=True, blank=True)
    field_type_18 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_18 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_18 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_18 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_18 = models.CharField(max_length=255, null=True, blank=True)

    values_19 = models.CharField(max_length=255, null=True, blank=True)
    field_code_19 = models.CharField(max_length=255, null=True, blank=True)
    field_type_19 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_19 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_19 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_19 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_19 = models.CharField(max_length=255, null=True, blank=True)

    values_20 = models.CharField(max_length=255, null=True, blank=True)
    field_code_20 = models.CharField(max_length=255, null=True, blank=True)
    field_type_20 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_20 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_20 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_20 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_20 = models.CharField(max_length=255, null=True, blank=True)

    values_21 = models.CharField(max_length=255, null=True, blank=True)
    field_code_21 = models.CharField(max_length=255, null=True, blank=True)
    field_type_21 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_21 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_21 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_21 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_21 = models.CharField(max_length=255, null=True, blank=True)

    values_22 = models.CharField(max_length=255, null=True, blank=True)
    field_code_22 = models.CharField(max_length=255, null=True, blank=True)
    field_type_22 = models.CharField(max_length=255, null=True, blank=True)
    parent_code_22 = models.CharField(max_length=255, null=True, blank=True)
    field_data_type_22 = models.CharField(max_length=255, null=True, blank=True)
    form_submission_field_22 = models.CharField(max_length=255, null=True, blank=True)
    human_readable_values_22 = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'events_extended'


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


