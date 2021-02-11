# Generated by Django 3.1.5 on 2021-02-06 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0002_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyPlanningRegistrations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.IntegerField(blank=True, null=True)),
                ('event_date', models.DateTimeField(blank=True, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('team', models.CharField(blank=True, max_length=100, null=True)),
                ('team_id', models.CharField(blank=True, max_length=100, null=True)),
                ('event_type', models.CharField(blank=True, max_length=100, null=True)),
                ('location_id', models.CharField(blank=True, max_length=100, null=True)),
                ('provider_id', models.CharField(blank=True, max_length=100, null=True)),
                ('base_entity_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'family_planning_registrations',
            },
        ),
    ]