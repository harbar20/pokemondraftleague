# Generated by Django 2.2.10 on 2020-04-07 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20200330_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='timezone',
            field=models.CharField(default='Not Specified', max_length=30),
        ),
    ]
