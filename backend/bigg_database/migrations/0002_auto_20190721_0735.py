# Generated by Django 2.2.3 on 2019-07-21 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bigg_database', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelreaction',
            name='subsystem',
            field=models.CharField(blank=True, max_length=127, null=True),
        ),
    ]