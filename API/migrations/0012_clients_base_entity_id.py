# Generated by Django 2.1.3 on 2020-11-18 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0011_referraltask_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='clients',
            name='base_entity_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
