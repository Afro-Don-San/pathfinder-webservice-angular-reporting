# Generated by Django 3.1.5 on 2021-02-06 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0005_auto_20210206_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familyplanningregistrations',
            name='client_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]