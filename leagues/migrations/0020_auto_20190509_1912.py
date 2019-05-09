# Generated by Django 2.1.7 on 2019-05-09 19:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0019_auto_20190509_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='coachdata',
            name='conference',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='leagues.conference_name'),
        ),
        migrations.AddField(
            model_name='coachdata',
            name='division',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='leagues.division_name'),
        ),
        migrations.AlterField(
            model_name='coachdata',
            name='teammate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teammate', to=settings.AUTH_USER_MODEL),
        ),
    ]
