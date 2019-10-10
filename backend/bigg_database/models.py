from django.db import models as _models

from .fields import JSONField


class Model(_models.Model):
    bigg_id = _models.CharField(unique=True, max_length=127, db_index=True)

    COMPARTMENTS_CHOICES = (
        ('c', 'cytosol'),
        ('e', 'extracellular space'),
        ('p', 'periplasm'),
        ('m', 'mitochondria'),
        ('x', 'peroxisome/glyoxysome'),
        ('r', 'endoplasmic reticulum'),
        ('v', 'vacuole'),
        ('n', 'nucleus'),
        ('g', 'golgi apparatus'),
        ('u', 'thylakoid'),
        ('l', 'lysosome'),
        ('h', 'chloroplast'),
        ('f', 'flagellum'),
        ('s', 'eyespot'),
        ('im', 'intermembrane space of mitochondria'),
        ('cx', 'carboxyzome'),
        ('um', 'thylakoid membrane'),
        ('cm', 'cytosolic membrane'),
        ('i', 'i'))

    compartments = JSONField()
    version = _models.CharField(max_length=127)

    class Meta:
        verbose_name = 'Model'


class Reaction(_models.Model):
    bigg_id = _models.CharField(max_length=127, unique=True, db_index=True)
    name = _models.CharField(max_length=255, blank=True)
    models = _models.ManyToManyField(
        Model, through='ModelReaction', through_fields=('reaction', 'model'))

    reaction_string = _models.CharField(max_length=7000)
    pseudoreaction = _models.BooleanField()

    database_links = JSONField()

    class Meta:
        verbose_name = 'Reaction'


class Metabolite(_models.Model):
    bigg_id = _models.CharField(unique=True, max_length=127, db_index=True)
    name = _models.CharField(max_length=511)

    reactions = _models.ManyToManyField(
        Reaction, through='ReactionMetabolite', through_fields=('metabolite', 'reaction'))
    models = _models.ManyToManyField(
        Model, through='ModelMetabolite', through_fields=('metabolite', 'model'))

    formulae = JSONField(max_length=127)
    charges = _models.IntegerField(blank=True, null=True)

    database_links = JSONField()

    class Meta:
        verbose_name = 'Metabolite'


class Gene(_models.Model):
    bigg_id = _models.CharField(unique=True, max_length=127, db_index=True)
    name = _models.CharField(max_length=127)
    rightpos = _models.IntegerField()
    leftpos = _models.IntegerField()
    chromosome_ncbi_accession = _models.CharField(default='', max_length=127)
    mapped_to_genbank = _models.BooleanField()

    strand = _models.CharField(max_length=127)
    protein_sequence = _models.TextField()
    dna_sequence = _models.TextField()

    genome_name = _models.CharField(max_length=127)
    genome_ref_string = _models.CharField(max_length=127)

    database_links = JSONField()

    reactions = _models.ManyToManyField(
        Reaction, through='ReactionGene', through_fields=('gene', 'reaction'))
    models = _models.ManyToManyField(Model)

    class Meta:
        constraints = [
            _models.CheckConstraint(check=_models.Q(rightpos__gte=_models.F('leftpos')),
                                    name='right_gte_left')
        ]

        verbose_name = 'Gene'


class ReactionGene(_models.Model):
    gene_reaction_rule = _models.TextField()

    reaction = _models.ForeignKey(Reaction, on_delete=_models.CASCADE)
    gene = _models.ForeignKey(Gene, on_delete=_models.CASCADE)

    class Meta:
        unique_together = ('reaction', 'gene')


class ReactionMetabolite(_models.Model):
    stoichiometry = _models.IntegerField()

    reaction = _models.ForeignKey(Reaction, on_delete=_models.CASCADE)
    metabolite = _models.ForeignKey(Metabolite, on_delete=_models.CASCADE)

    class Meta:
        unique_together = ('reaction', 'metabolite')


class ModelMetabolite(_models.Model):
    organism = _models.CharField(max_length=127)

    model = _models.ForeignKey(Model, on_delete=_models.CASCADE)
    metabolite = _models.ForeignKey(Metabolite, on_delete=_models.CASCADE)

    class Meta:
        unique_together = ('model', 'metabolite')


class ModelReaction(_models.Model):
    organism = _models.CharField(max_length=127)

    lower_bound = _models.FloatField()
    upper_bound = _models.FloatField()

    subsystem = _models.CharField(max_length=127, blank=True, null=True)

    gene_reaction_rule = _models.TextField()

    model = _models.ForeignKey(Model, on_delete=_models.CASCADE)
    reaction = _models.ForeignKey(Reaction, on_delete=_models.CASCADE)

    class Meta:
        unique_together = ('model', 'reaction')
        constraints = [
            _models.CheckConstraint(check=_models.Q(upper_bound__gte=_models.F('lower_bound')),
                                    name='upper_gte_lower')
        ]
