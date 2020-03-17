# Generated by Django 2.2.10 on 2020-03-13 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0071_auto_20200309_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='teamlogo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, default='team_logos/defaultteamlogo.png', null=True, upload_to='team_logos')),
            ],
        ),
        migrations.AddField(
            model_name='coachdata',
            name='logo2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='leagues.teamlogo'),
        ),
    ]