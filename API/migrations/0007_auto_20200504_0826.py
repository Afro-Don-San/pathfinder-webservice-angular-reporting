# Generated by Django 2.1.3 on 2020-05-04 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0006_auto_20200502_2049'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='date_of_birth',
            new_name='birthDate',
        ),
        migrations.RenameField(
            model_name='client',
            old_name='date_created',
            new_name='dateCreated',
        ),
        migrations.RenameField(
            model_name='client',
            old_name='first_name',
            new_name='firstName',
        ),
        migrations.RenameField(
            model_name='client',
            old_name='last_name',
            new_name='lastName',
        ),
        migrations.RenameField(
            model_name='client',
            old_name='middle_name',
            new_name='middleName',
        ),
    ]