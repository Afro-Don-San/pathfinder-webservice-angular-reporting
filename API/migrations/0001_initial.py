# Generated by Django 2.1.3 on 2020-05-22 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(blank=True, max_length=255, null=True)),
                ('middleName', models.CharField(blank=True, max_length=255, null=True)),
                ('lastName', models.CharField(blank=True, max_length=255, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Female', 'Female'), ('Male', 'Male')], max_length=30, null=True)),
                ('date_of_birth', models.DateField(auto_now_add=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edited', models.DateTimeField(blank=True, null=True)),
                ('city_village', models.CharField(blank=True, default='unknown', max_length=255, null=True)),
                ('landmark', models.CharField(blank=True, default='unknown', max_length=255, null=True)),
                ('type', models.CharField(blank=True, default='Client', max_length=100, null=True)),
            ],
            options={
                'db_table': 'Client',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('Referral', 'Referral'), ('Family Registration', 'Family Registration'), ('Family Planning Registration', 'Family Planning Registration'), ('Family Member Registration', 'Family Member Registration')], max_length=30)),
                ('provider_id', models.CharField(max_length=255)),
                ('event_date', models.DateTimeField()),
                ('team', models.CharField(max_length=255)),
                ('team_id', models.CharField(max_length=255)),
                ('location_id', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Event',
            },
        ),
    ]
