# Generated by Django 2.2.5 on 2019-10-17 13:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biobricks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='biobrick',
            name='url',
        ),
    ]