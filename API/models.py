from django.db import models


# Create your models here.
class Client(models.Model):
    def __str__(self):
        return '%d' % self.id

    Female = 'Female'
    Male = 'Male'

    GENDER_TYPE_CHOICES = (
        (Female, 'Female'),
        (Male, 'Male')
    )

    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name =  models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_TYPE_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(auto_now_add=True, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    city_village = models.CharField(max_length=255, default='unknown', null=True, blank=True)
    landmark = models.CharField(max_length=255, default='unknown', null=True, blank=True)
    type = models.CharField(max_length=100, default='Client', null=True, blank=True)

    class Meta:
        db_table = 'Client'


class Event(models.Model):
    def __str__(self):
        return '%d' % self.id

    referral = 'Referral'
    family_registration = 'Family Registration'
    family_planning_registration = 'Family Planning Registration'
    family_member_registration = 'Family Member Registration'

    EVENT_TYPE_CHOICES = (
        (referral, 'Referral'),
        (family_registration, 'Family Registration'),
        (family_planning_registration, 'Family Planning Registration'),
        (family_member_registration, 'Family Member Registration')
    )

    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    provider_id = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    team = models.CharField(max_length=255)
    team_id = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Event'

