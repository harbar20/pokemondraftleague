# Generated by Django 2.1.7 on 2019-06-17 19:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0005_auto_20190614_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='draft',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='draftpicks', to='leagues.coachdata'),
        ),
    ]
