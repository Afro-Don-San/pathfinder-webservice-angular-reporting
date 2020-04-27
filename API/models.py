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
    date_created = models.DateField(auto_now_add=True)
    date_edited = models.DateField(null=True, blank=True)
    city_village = models.CharField(max_length=255, default='unknown')
    landmark = models.CharField(max_length=255, default='unknown')
    type = models.CharField(max_length=100, default='Client')

    class Meta:
        db_table = 'Client'
