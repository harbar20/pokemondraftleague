# Generated by Django 2.1.7 on 2019-05-03 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_sitesettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='sprite',
            field=models.CharField(choices=[('xyani.gif', 'XY Animated'), ('xyani-shiny.gif', 'XY Shiny Animated'), ('bwani.png', 'BW'), ('bwani-shiny.png', 'BW Shiny')], default='xyani', max_length=10),
        ),
    ]
