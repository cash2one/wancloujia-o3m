'''
from haystack import indexes
from models import AD

class ADIndex(indexes.ModelSearchIndex, indexes.Indexable):

    class Meta:
        model = AD

'''
