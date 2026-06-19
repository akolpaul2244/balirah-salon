from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Service, ServiceCategory
from .serializers import ServiceSerializer, ServiceCategorySerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'duration_minutes', 'name']

    def get_queryset(self):
        return Service.objects.filter(is_active=True).select_related('category')


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
