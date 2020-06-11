from django.db import models
from datetime import datetime


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

    _id = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_TYPE_CHOICES, null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    city_village = models.CharField(max_length=255, default='unknown', null=True, blank=True)
    landmark = models.CharField(max_length=255, default='unknown', null=True, blank=True)
    type = models.CharField(max_length=100, default='Client', null=True, blank=True)

    class Meta:
        db_table = 'Clients'


class Event(models.Model):
    def __str__(self):
        return '%d' % self.id

    family_member_registration = 'Family Member Registration'
    family_planning_registration = 'Family Planning Registration'
    introduction_to_family_planning = 'Introduction to Family Planning'
    family_planning_pregnancy_screening = 'Family Planning Pregnancy Screening'
    family_planning_method_choice = 'Family Planning Method Choice'
    give_family_planning_method = 'Give Family Planning Method'
    update_family_planning_registration = 'Update Family planning Registration'
    family_planning_change_method = 'Family Planning Change Method'
    fp_follow_up_visit = 'Fp Follow Up Visit'
    fp_follow_up_visit_resupply = 'Fp Follow Up Visit Resupply'
    fp_follow_up_visit_counselling = 'Fp Follow Up Visit Counselling'
    family_planning_discontinuation = 'Family Planning Discontinuation'
    anc_referral = 'ANC Referral'
    family_planning_referral = 'Family Planning Referral'
    family_planning_referral_followup = 'Family Planning Referral Followup'

    EVENT_TYPE_CHOICES = (
        (family_member_registration, 'Family Member Registration'),
        (family_planning_registration, 'Family Planning Registration'),
        (introduction_to_family_planning, 'Introduction to Family Planning'),
        (family_planning_pregnancy_screening, 'Family Planning Pregnancy Screening'),
        (family_planning_method_choice, 'Family Planning Method Choice'),
        (give_family_planning_method, 'Give Family Planning Method'),
        (update_family_planning_registration, 'Update Family planning Registration'),
        (family_planning_change_method, 'Family Planning Change Method'),
        (fp_follow_up_visit, 'Fp Follow Up Visit'),
        (fp_follow_up_visit_resupply, 'Fp Follow Up Visit Resupply'),
        (fp_follow_up_visit_counselling, 'Fp Follow Up Visit Counselling'),
        (family_planning_discontinuation, 'Family Planning Discontinuation'),
        (anc_referral, 'ANC Referral'),
        (family_planning_referral, 'Family Planning Referral'),
        (family_planning_referral_followup, 'Family Planning Referral Followup')

    )

    _id = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    event_type = models.CharField(max_length=100, choices=EVENT_TYPE_CHOICES, null=True, blank=True)
    entity_type = models.CharField(max_length=255, null=True, blank=True)
    team = models.CharField(max_length=255, null=True, blank=True)
    team_id = models.CharField(max_length=255, null=True, blank=True)
    location_id = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'Events'

