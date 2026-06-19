from rest_framework import serializers
from .models import ServiceCategory, Service


class ServiceSerializer(serializers.ModelSerializer):
    price_display = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'description', 'short_description', 'price', 'price_max',
            'price_display', 'duration_minutes', 'duration_display',
            'is_featured', 'reengagement_category',
        ]


class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'category_type', 'description', 'icon', 'services']
