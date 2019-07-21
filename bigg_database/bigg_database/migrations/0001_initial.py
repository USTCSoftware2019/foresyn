# Generated by Django 2.2.3 on 2019-07-20 13:13

import bigg_database.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Metabolite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('name', models.CharField(max_length=127)),
                ('formulae', models.CharField(max_length=127)),
                ('charges', models.IntegerField(blank=True, null=True)),
                ('database_links', bigg_database.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('compartments', bigg_database.fields.JSONField()),
                ('version', models.CharField(max_length=127)),
            ],
        ),
        migrations.CreateModel(
            name='ModelReaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organism', models.CharField(max_length=127)),
                ('lower_bound', models.FloatField()),
                ('upper_bound', models.FloatField()),
                ('subsystem', models.CharField(max_length=127)),
                ('gene_reaction_rule', models.CharField(max_length=127)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Model')),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('name', models.CharField(blank=True, max_length=127)),
                ('reaction_string', models.CharField(max_length=1023)),
                ('pseudoreaction', models.BooleanField()),
                ('database_links', bigg_database.fields.JSONField()),
                ('models', models.ManyToManyField(through='bigg_database.ModelReaction', to='bigg_database.Model')),
            ],
        ),
        migrations.CreateModel(
            name='ReactionMetabolite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stoichiometry', models.IntegerField()),
                ('metabolite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Metabolite')),
                ('reaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Reaction')),
            ],
        ),
        migrations.AddField(
            model_name='modelreaction',
            name='reaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Reaction'),
        ),
        migrations.CreateModel(
            name='ModelMetabolite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organism', models.CharField(max_length=127)),
                ('metabolite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Metabolite')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Model')),
            ],
        ),
        migrations.AddField(
            model_name='metabolite',
            name='models',
            field=models.ManyToManyField(through='bigg_database.ModelMetabolite', to='bigg_database.Model'),
        ),
        migrations.AddField(
            model_name='metabolite',
            name='reactions',
            field=models.ManyToManyField(through='bigg_database.ReactionMetabolite', to='bigg_database.Reaction'),
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('name', models.CharField(max_length=127)),
                ('models', models.ManyToManyField(to='bigg_database.Model')),
            ],
        ),
    ]
