from bigg_database.models import Gene, Model, Metabolite, Reaction
from haystack import indexes


class ModelIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    bigg_id = indexes.CharField(model_attr='bigg_id')

    def get_model(self):
        return Model

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class ReactionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    bigg_id = indexes.CharField(model_attr='bigg_id')
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Reaction

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class MetaboliteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    bigg_id = indexes.CharField(model_attr='bigg_id')
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Metabolite

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class GeneIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    bigg_id = indexes.CharField(model_attr='bigg_id')
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return Gene

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
