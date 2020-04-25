from django.db import models


# Create your models here.

class Client(models.Model):
    def __str__(self):
        return '%d' % self.id

    first_name = models.CharField(max_length=255)
    middle_name =  models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()

    class Meta:
        db_table = 'Client'
