'''
from haystack import indexes
from models import Company, Store, Staff

class CompanyIndex(indexes.ModelSearchIndex, indexes.Indexable):

    class Meta:
        model = Company


class StoreIndex(indexes.ModelSearchIndex, indexes.Indexable):

    class Meta:
        model = Store


class StaffIndex(indexes.ModelSearchIndex, indexes.Indexable):

    class Meta:
        model = Staff
'''
