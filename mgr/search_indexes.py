from haystack import indexes
from models import Company, Store

class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')
    code = indexes.CharField(model_attr='code')

    def get_model(self):
        return Company

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class StoreIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')
    code = indexes.CharField(model_attr='code')

    def get_model(self):
        return Store

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

