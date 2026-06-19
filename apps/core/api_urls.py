from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.services.api_views import ServiceViewSet, ServiceCategoryViewSet
from apps.bookings.api_views import AppointmentViewSet, AvailableSlotsView
from apps.team.api_views import StylistViewSet
from apps.testimonials.api_views import TestimonialViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'stylists', StylistViewSet, basename='stylist')
router.register(r'testimonials', TestimonialViewSet, basename='testimonial')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('slots/', AvailableSlotsView.as_view(), name='available-slots'),
]
