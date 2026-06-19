from rest_framework import serializers, viewsets
from rest_framework.permissions import AllowAny
from .models import Stylist


class StylistSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    specialization_names = serializers.SerializerMethodField()

    class Meta:
        model = Stylist
        fields = [
            'id', 'full_name', 'slug', 'role', 'role_display',
            'bio', 'years_experience', 'specialization_names', 'instagram',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_specialization_names(self, obj):
        return list(obj.specializations.values_list('name', flat=True))


class StylistViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StylistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Stylist.objects.filter(is_active=True).prefetch_related('specializations')
        service_id = self.request.query_params.get('service')
        if service_id:
            from apps.services.models import Service
            try:
                service = Service.objects.get(pk=service_id, is_active=True)
                qs = qs.filter(specializations=service.category)
            except Service.DoesNotExist:
                return qs.none()
        return qs
