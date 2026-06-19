from rest_framework import serializers, viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True, default='')

    class Meta:
        model = Testimonial
        fields = ['id', 'client_name', 'service_name', 'rating', 'body', 'created_at']
        read_only_fields = ['created_at']


class TestimonialViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Testimonial.objects.filter(is_approved=True).select_related('service')

    def perform_create(self, serializer):
        user = self.request.user
        name = user.get_full_name() if user.is_authenticated else serializer.validated_data.get('client_name', '')
        serializer.save(
            user=user if user.is_authenticated else None,
            client_name=name,
            is_approved=False,
        )
