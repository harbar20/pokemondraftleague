# Generated by Django 2.2.10 on 2020-10-25 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0078_discord_settings_matchreminderchannel'),
    ]

    operations = [
        migrations.AddField(
            model_name='draft',
            name='announced',
            field=models.BooleanField(default=False),
        ),
    ]
