from rest_framework import serializers
from django.conf import settings
from django.utils import timezone


class FileField(serializers.FileField):
    def to_representation(self, value):
        if value and hasattr(value, 'url'):
            return settings.MEDIA_URL + value.name
        return None


class BaseSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=timezone.now, read_only=True)


class CreateUpdateMixin:
    def create(self, validated_data):
        # import pdb;pdb.set_trace()
        if 'user' in [field.name for field in self.Meta.model._meta.get_fields()]:

            validated_data['user'] = self.context['request'].user

        validated_data['created_by'] = self.context['request'].user

        validated_data['created_at'] = timezone.now()
        # import pdb;pdb.set_trace()

        instance = self.Meta.model.objects.create(**validated_data)

        return instance

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user

        validated_data['updated_at'] = timezone.now()

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance
