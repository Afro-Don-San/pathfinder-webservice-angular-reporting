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
    def __str__(self):
        return '%d' % self.id

    date_time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events_extended'
