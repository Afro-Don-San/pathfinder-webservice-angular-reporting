# Generated by Django 2.1.3 on 2020-08-31 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0003_referral_referraltask'),
    ]

    operations = [
        migrations.RenameField(
            model_name='referraltask',
            old_name='for_entity',
            new_name='chw_id',
        ),
        migrations.RenameField(
            model_name='referraltask',
            old_name='location',
            new_name='chw_name',
        ),
        migrations.RenameField(
            model_name='referraltask',
            old_name='owner',
            new_name='health_facility_location_id',
        ),
        migrations.RenameField(
            model_name='referraltask',
            old_name='reasonReference',
            new_name='referral_formsubmissionid',
        ),
        migrations.RenameField(
            model_name='referraltask',
            old_name='requester',
            new_name='referred_client_base_entity_id',
        ),
    ]
