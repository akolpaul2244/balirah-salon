from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.accounts.models import User
from apps.services.models import ServiceCategory, Service
from apps.team.models import Stylist
from .models import Appointment, TimeSlot
from .services import get_available_slots, create_appointment


class AppointmentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='client@example.com', password='Pass123!',
            first_name='Test', last_name='Client', phone_number='+256700000001'
        )
        self.category = ServiceCategory.objects.create(
            name='Barber', slug='barber', category_type='barber', order=1
        )
        self.service = Service.objects.create(
            category=self.category, name='Haircut', slug='haircut',
            description='desc', price=15000, duration_minutes=30,
            reengagement_category='haircut'
        )
        self.stylist = Stylist.objects.create(
            first_name='Brian', last_name='Test', slug='brian-test', role='barber'
        )
        self.stylist.specializations.add(self.category)
        self.slot = TimeSlot.objects.create(
            stylist=self.stylist,
            date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(9, 30),
            is_available=False,
        )
        self.appointment = Appointment.objects.create(
            user=self.user,
            service=self.service,
            stylist=self.stylist,
            time_slot=self.slot,
            appointment_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(9, 30),
            status='confirmed',
        )

    def test_appointment_reference_generated(self):
        self.assertTrue(self.appointment.reference.startswith('BAL'))
        self.assertEqual(len(self.appointment.reference), 10)

    def test_client_name_from_user(self):
        self.assertEqual(self.appointment.client_name, 'Test Client')

    def test_client_phone_from_user(self):
        self.assertEqual(self.appointment.client_phone, '+256700000001')

    def test_is_upcoming_true(self):
        self.assertTrue(self.appointment.is_upcoming)

    def test_can_cancel_true(self):
        self.assertTrue(self.appointment.can_cancel)

    def test_cannot_cancel_past(self):
        self.appointment.appointment_date = timezone.localdate() - timedelta(days=1)
        self.assertFalse(self.appointment.can_cancel)


class AvailableSlotsAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Barber', slug='barber2', category_type='barber', order=1
        )
        self.service = Service.objects.create(
            category=self.category, name='Cut', slug='cut',
            description='desc', price=15000, duration_minutes=30,
        )
        self.stylist = Stylist.objects.create(
            first_name='Test', last_name='Stylist', slug='test-stylist', role='barber'
        )
        self.stylist.specializations.add(self.category)

    def test_slots_endpoint_requires_service_and_date(self):
        response = self.client.get(reverse('bookings:api_slots'))
        self.assertEqual(response.status_code, 400)

    def test_slots_endpoint_returns_list(self):
        future_date = (timezone.localdate() + timedelta(days=2)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse('bookings:api_slots'),
            {'service': self.service.pk, 'date': future_date}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('slots', response.json())

    def test_past_date_returns_empty(self):
        past_date = (timezone.localdate() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse('bookings:api_slots'),
            {'service': self.service.pk, 'date': past_date}
        )
        self.assertEqual(response.json()['slots'], [])
