# Generated by Django 4.0.5 on 2022-12-06 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_acount_acount_onesignalid'),
    ]

    operations = [
        migrations.AddField(
            model_name='acount',
            name='acount_notificated',
            field=models.BooleanField(default=False),
        ),
    ]
