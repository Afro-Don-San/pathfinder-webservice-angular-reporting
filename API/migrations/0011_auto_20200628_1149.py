# Generated by Django 2.1.3 on 2020-06-28 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0010_auto_20200628_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventextended',
            name='event_date',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
