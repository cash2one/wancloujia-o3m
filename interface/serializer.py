__author__ = 'bridge'
from django.forms import widgets
from rest_framework import serializers
from interface.models import LogEntity

class LogSerializer(serializers.Serializer):
    pk = serializers.Field()  # Note: `Field` is an untyped read-only field.
    content = serializers.CharField(max_length=10240, default='')
    create = serializers.DateTimeField()

    def restore_object(self, attrs, instance=None):
        """
        Create or update a new snippet instance, given a dictionary
        of deserialized field values.

        Note that if we don't define this method, then deserializing
        data will simply return a dictionary of items.
        """
        if instance:
            # Update existing instance
            instance.content = attrs.get('content', instance.content)
            instance.create = attrs.get('create', instance.create)
            return instance

        # Create new instance
        return LogEntity(**attrs)