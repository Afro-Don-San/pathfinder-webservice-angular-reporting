# Generated by Django 2.1.3 on 2020-06-09 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0006_auto_20200609_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='date_created',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='date_edited',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]