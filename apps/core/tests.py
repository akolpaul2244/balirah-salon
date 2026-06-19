from django.test import TestCase, Client
from django.urls import reverse
from .models import SalonSettings, OpeningHours, ContactMessage


class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        SalonSettings.objects.create(pk=1, salon_name='Balirah Beauty Salon')

    def test_home_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_about_view(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_get(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_post_valid(self):
        response = self.client.post(reverse('core:contact'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test enquiry',
            'message': 'Hello, I would like to know more about your services.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_post_invalid(self):
        response = self.client.post(reverse('core:contact'), {
            'name': '',
            'email': 'not-an-email',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_privacy_policy_view(self):
        response = self.client.get(reverse('core:privacy_policy'))
        self.assertEqual(response.status_code, 200)

    def test_terms_conditions_view(self):
        response = self.client.get(reverse('core:terms_conditions'))
        self.assertEqual(response.status_code, 200)


class SalonSettingsModelTests(TestCase):
    def test_singleton_get(self):
        s = SalonSettings.get()
        s2 = SalonSettings.get()
        self.assertEqual(s.pk, s2.pk)
        self.assertEqual(SalonSettings.objects.count(), 1)

    def test_str(self):
        s = SalonSettings.get()
        self.assertEqual(str(s), s.salon_name)
