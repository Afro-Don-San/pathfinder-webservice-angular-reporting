# Generated by Django 2.1.3 on 2020-06-26 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0006_auto_20200626_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventextended',
            name='values_0',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
