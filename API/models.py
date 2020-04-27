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

    first_name = models.CharField(max_length=255)
    middle_name =  models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=30, choices=GENDER_TYPE_CHOICES)
    date_of_birth = models.DateField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    city_village = models.CharField(max_length=255, default='unknown')
    landmark = models.CharField(max_length=255, default='unknown')
    type = models.CharField(max_length=100, default='Client')

    class Meta:
        db_table = 'Client'


class Event(models.Model):
    def __str__(self):
        return '%d' % self.id

    referral = 'Referral'
    family_planning = 'Family Planning'

    EVENT_TYPE_CHOICES = (
        (referral, 'Referral'),
        (family_planning, 'Family Planning')
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

