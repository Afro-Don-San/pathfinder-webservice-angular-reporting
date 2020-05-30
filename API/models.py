from django.db import models


# Create your models here.
class FamilyPlanningRegistration(models.Model):
    def __str__(self):
        return '%d' % self.id

    Female = 'Female'
    Male = 'Male'

    GENDER_TYPE_CHOICES = (
        (Female, 'Female'),
        (Male, 'Male')
    )

    firstName = models.CharField(max_length=255, null=True, blank=True)
    middleName = models.CharField(max_length=255, null=True, blank=True)
    lastName = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_TYPE_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(auto_now_add=True, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    city_village = models.CharField(max_length=255, default='unknown', null=True, blank=True)
    landmark = models.CharField(max_length=255, default='unknown', null=True, blank=True)
    type = models.CharField(max_length=100, default='Client', null=True, blank=True)

    class Meta:
        db_table = 'FamilyPlanningRegistrations'


class Referral(models.Model):
    def __str__(self):
        return '%d' % self.id

    fp_referral = 'Family Planning Referral'
    other_referral = 'Other Referral'

    REFERRAL_TYPE_CHOICES = (
        (fp_referral, 'Family Planning Referral'),
        (other_referral, 'Other Referral'),
    )

    provider_id = models.CharField(max_length=255)
    referral_date = models.DateTimeField()
    referral_type = models.CharField(max_length=100, choices=REFERRAL_TYPE_CHOICES, null=True, blank=True)
    team = models.CharField(max_length=255)
    team_id = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Referrals'



