# Generated by Django 2.1.3 on 2020-06-10 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0007_auto_20200609_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='birth_date',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='date_created',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='date_edited',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]