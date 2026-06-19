from django.test import TestCase, Client
from django.urls import reverse
from .models import ServiceCategory, Service


class ServiceModelTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Barber Services', slug='barber-services', category_type='barber', order=1
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Classic Haircut',
            slug='classic-haircut',
            description='A classic haircut.',
            price=15000,
            duration_minutes=30,
        )

    def test_service_str(self):
        self.assertEqual(str(self.service), 'Classic Haircut')

    def test_price_display(self):
        self.assertIn('15,000', self.service.price_display)

    def test_duration_display_minutes(self):
        self.assertEqual(self.service.duration_display, '30min')

    def test_duration_display_hours(self):
        self.service.duration_minutes = 90
        self.assertEqual(self.service.duration_display, '1h 30min')

    def test_slug_auto_generated(self):
        service = Service.objects.create(
            category=self.category,
            name='Hot Towel Shave',
            description='desc',
            price=20000,
            duration_minutes=40,
        )
        self.assertEqual(service.slug, 'hot-towel-shave')

    def test_price_display_with_max(self):
        self.service.price_max = 45000
        self.assertIn('–', self.service.price_display)


class ServiceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Barber Services', slug='barber-services', category_type='barber', order=1
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Classic Haircut',
            slug='classic-haircut',
            description='A classic haircut.',
            price=15000,
            duration_minutes=30,
            is_active=True,
        )

    def test_service_list_view(self):
        response = self.client.get(reverse('services:list'))
        self.assertEqual(response.status_code, 200)

    def test_service_detail_view(self):
        response = self.client.get(reverse('services:detail', kwargs={'slug': 'classic-haircut'}))
        self.assertEqual(response.status_code, 200)

    def test_service_detail_404_inactive(self):
        self.service.is_active = False
        self.service.save()
        response = self.client.get(reverse('services:detail', kwargs={'slug': 'classic-haircut'}))
        self.assertEqual(response.status_code, 404)
