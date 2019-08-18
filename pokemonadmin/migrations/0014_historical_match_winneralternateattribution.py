# Generated by Django 2.1.7 on 2019-07-26 17:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pokemonadmin', '0013_auto_20190726_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='historical_match',
            name='winneralternateattribution',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='historicwinneralternateattribution', to=settings.AUTH_USER_MODEL),
        ),
    ]
