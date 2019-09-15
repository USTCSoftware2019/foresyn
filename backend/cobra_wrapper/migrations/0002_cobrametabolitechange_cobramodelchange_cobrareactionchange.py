# Generated by Django 2.2.5 on 2019-09-13 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cobra_wrapper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CobraReactionChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fields', models.CharField(blank=True, max_length=200)),
                ('previous_values', models.TextField(blank=True)),
                ('values', models.TextField(blank=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraReaction')),
            ],
            options={
                'verbose_name': 'reaction_change',
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='CobraModelChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fields', models.CharField(blank=True, max_length=200)),
                ('previous_values', models.TextField(blank=True)),
                ('values', models.TextField(blank=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraModel')),
            ],
            options={
                'verbose_name': 'model_change',
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='CobraMetaboliteChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fields', models.CharField(blank=True, max_length=200)),
                ('previous_values', models.TextField(blank=True)),
                ('values', models.TextField(blank=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraMetabolite')),
            ],
            options={
                'verbose_name': 'metabolite_change',
                'ordering': ['-time'],
            },
        ),
    ]