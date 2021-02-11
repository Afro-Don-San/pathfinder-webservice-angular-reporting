from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from Core import models as core_models



# Create your models here.
class Profile(models.Model):
    def __str__(self):
        return '%s' % self.user.id

    Female = 'Female'
    Male = 'Male'

    GENDER_TYPE_CHOICES = (
        (Female, 'Female'),
        (Male, 'Male')
    )

    date_time_created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=30, choices=GENDER_TYPE_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    location = models.ForeignKey(core_models.Location, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'UserProfiles'


class TokenModel(models.Model):
    key = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=100)

    class Meta:
        db_table = 'UserTokens'


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()




