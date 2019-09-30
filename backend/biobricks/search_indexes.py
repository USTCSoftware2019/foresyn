from haystack import indexes
from .models import Biobrick


class BiobrickIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    description = indexes.CharField(model_attr="description")
    keywords = indexes.CharField(model_attr="key_words")
    part_name = indexes.CharField(model_attr="part_name")

    def get_model(self):
        return Biobrick

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
