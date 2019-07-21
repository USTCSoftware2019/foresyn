# Generated by Django 2.2.3 on 2019-07-21 11:15

import bigg_database.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bigg_database', '0002_auto_20190721_0735'),
    ]

    operations = [
        migrations.AddField(
            model_name='gene',
            name='chromosome_ncbi_accession',
            field=models.CharField(default='', max_length=127),
        ),
        migrations.AddField(
            model_name='gene',
            name='database_links',
            field=bigg_database.fields.JSONField(default='{}'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='dna_sequence',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='genome_name',
            field=models.CharField(default='', max_length=127),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='genome_ref_string',
            field=models.CharField(default='', max_length=127),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='leftpos',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='mapped_to_genbank',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='protein_sequence',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='rightpos',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gene',
            name='strand',
            field=models.CharField(default='', max_length=127),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ReactionGene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_reaction_rule', models.CharField(max_length=127)),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Gene')),
                ('reaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigg_database.Reaction')),
            ],
        ),
        migrations.AddField(
            model_name='gene',
            name='reactions',
            field=models.ManyToManyField(through='bigg_database.ReactionGene', to='bigg_database.Reaction'),
        ),
    ]
