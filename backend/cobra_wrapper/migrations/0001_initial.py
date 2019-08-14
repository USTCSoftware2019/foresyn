# Generated by Django 2.2.4 on 2019-08-14 10:38

import cobra_wrapper.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CobraMetabolite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cobra_id', models.CharField(max_length=511)),
                ('name', models.CharField(blank=True, default='', max_length=511)),
                ('formula', models.CharField(max_length=127)),
                ('charge', models.FloatField()),
                ('compartment', models.CharField(blank=True, default='', max_length=50)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'metabolite',
                'ordering': ['cobra_id', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CobraReaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cobra_id', models.CharField(max_length=511)),
                ('name', models.CharField(blank=True, default='', max_length=511)),
                ('subsystem', models.CharField(blank=True, default='', max_length=127, null=True)),
                ('lower_bound', models.FloatField(default=0.0)),
                ('upper_bound', models.FloatField(blank=True, default=None, null=True)),
                ('coefficients', models.TextField(default='', validators=[cobra_wrapper.models.validate_coefficients_space_splited_text])),
                ('gene_reaction_rule', models.TextField(blank=True, default='')),
                ('metabolites', models.ManyToManyField(blank=True, to='cobra_wrapper.CobraMetabolite')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'reaction',
                'ordering': ['cobra_id', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CobraModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cobra_id', models.CharField(max_length=127)),
                ('name', models.CharField(blank=True, default='', max_length=127)),
                ('objective', models.CharField(blank=True, default='', max_length=50)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('reactions', models.ManyToManyField(blank=True, to='cobra_wrapper.CobraReaction')),
            ],
            options={
                'verbose_name': 'model',
                'ordering': ['cobra_id', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CobraFva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.TextField(blank=True, default='')),
                ('loopless', models.BooleanField(blank=True, default=False)),
                ('fraction_of_optimum', models.FloatField(blank=True, default=1.0)),
                ('pfba_factor', models.NullBooleanField(default=None)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('task_id', models.UUIDField()),
                ('result', models.TextField(blank=True, default='', validators=[cobra_wrapper.models.validate_json_str_or_blank_str])),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraModel')),
                ('reaction_list', models.ManyToManyField(blank=True, to='cobra_wrapper.CobraReaction')),
            ],
            options={
                'verbose_name': 'fva',
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='CobraFba',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.TextField(blank=True, default='')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('task_id', models.UUIDField()),
                ('result', models.TextField(blank=True, default='', validators=[cobra_wrapper.models.validate_json_str_or_blank_str])),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraModel')),
            ],
            options={
                'verbose_name': 'fba',
                'ordering': ['-start_time'],
            },
        ),
    ]
