# Generated by Django 2.2.5 on 2019-10-11 15:29

import bigg_database.fields
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('name', models.CharField(max_length=127)),
                ('rightpos', models.IntegerField()),
                ('leftpos', models.IntegerField()),
                ('chromosome_ncbi_accession', models.CharField(default='', max_length=127)),
                ('mapped_to_genbank', models.BooleanField()),
                ('strand', models.CharField(max_length=127)),
                ('protein_sequence', models.TextField()),
                ('dna_sequence', models.TextField()),
                ('genome_name', models.CharField(max_length=127)),
                ('genome_ref_string', models.CharField(max_length=127)),
                ('database_links', bigg_database.fields.JSONField()),
            ],
            options={
                'verbose_name': 'Gene',
            },
        ),
        migrations.CreateModel(
            name='Metabolite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('name', models.CharField(max_length=511)),
                ('formulae', bigg_database.fields.JSONField(max_length=127)),
                ('charges', models.IntegerField(blank=True, null=True)),
                ('database_links', bigg_database.fields.JSONField()),
            ],
            options={
                'verbose_name': 'Metabolite',
            },
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('compartments', bigg_database.fields.JSONField()),
                ('version', models.CharField(max_length=127)),
            ],
            options={
                'verbose_name': 'Model',
            },
        ),
        migrations.CreateModel(
            name='ModelReaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organism', models.CharField(max_length=127)),
                ('lower_bound', models.FloatField()),
                ('upper_bound', models.FloatField()),
                ('subsystem', models.CharField(blank=True, max_length=127, null=True)),
                ('gene_reaction_rule', models.TextField()),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Model')),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bigg_id', models.CharField(db_index=True, max_length=127, unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('reaction_string', models.CharField(max_length=7000)),
                ('pseudoreaction', models.BooleanField()),
                ('database_links', bigg_database.fields.JSONField()),
                ('models', models.ManyToManyField(through='bigg_database.ModelReaction', to='bigg_database.Model')),
            ],
            options={
                'verbose_name': 'Reaction',
            },
        ),
        migrations.CreateModel(
            name='ReactionMetabolite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stoichiometry', models.IntegerField()),
                ('metabolite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Metabolite')),
                ('reaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Reaction')),
            ],
            options={
                'unique_together': {('reaction', 'metabolite')},
            },
        ),
        migrations.CreateModel(
            name='ReactionGene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_reaction_rule', models.TextField()),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Gene')),
                ('reaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Reaction')),
            ],
            options={
                'unique_together': {('reaction', 'gene')},
            },
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
        migrations.AddField(
            model_name='gene',
            name='models',
            field=models.ManyToManyField(to='bigg_database.Model'),
        ),
        migrations.AddField(
            model_name='gene',
            name='reactions',
            field=models.ManyToManyField(through='bigg_database.ReactionGene', to='bigg_database.Reaction'),
        ),
        migrations.AddConstraint(
            model_name='modelreaction',
            constraint=models.CheckConstraint(check=models.Q(upper_bound__gte=django.db.models.expressions.F('lower_bound')), name='upper_gte_lower'),
        ),
        migrations.AlterUniqueTogether(
            name='modelreaction',
            unique_together={('model', 'reaction')},
        ),
        migrations.AlterUniqueTogether(
            name='modelmetabolite',
            unique_together={('model', 'metabolite')},
        ),
        migrations.AddConstraint(
            model_name='gene',
            constraint=models.CheckConstraint(check=models.Q(rightpos__gte=django.db.models.expressions.F('leftpos')), name='right_gte_left'),
        ),
    ]
