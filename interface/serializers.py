from rest_framework import serializers
from app.models import App, UploadApk, Category, Subject


class AppSerializer(serializers.ModelSerializer):
    """
    apk = serializers.ForeignKey(UploadApk)
    name = serializers.CharField(max_length=20)
    package = serializers.CharField(max_length=100, unique=True)
    category = serializers.ForeignKey(Category)
    app_icon = serializers.CharField(max_length=100)
    version = serializers.CharField(max_length=20)
    popularize = serializers.BooleanField()
    create_date = serializers.DateTimeField(auto_now_add=True)
    online = serializers.BooleanField()
    desc = serializers.CharField(max_length=50)

    def restore_object(self, attrs, instance=None):
        if instance:
            instance.apk = attrs.get('apk', instance.apk)
            instance.name = attrs.get('name', instance.name)
            instance.package = attrs.get('package', instance.package)
            instance.category = attrs.get('category', instance.category)
            instance.app_icon = attrs.get('app_icon', instance.app_icon)
            instance.version = attrs.get('version', instance.version)
            instance.popularize = attrs.get('popularize', instance.popularize)
            instance.create_date = attrs.get('create_date', instance.create_date)
            instance.online = attrs.get('online', instance.online)
            instance.desc = attrs.get('desc', instance.desc)
            return instance
        return App(**attrs)
    """
    class Meta:
        model = App


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject