from django.test import TestCase, Client
from django.urls import reverse
from .models import User


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            phone_number='+256700000001',
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), 'test@example.com')

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Test User')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='pass')


class AuthViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='view@example.com',
            password='SecurePass123!',
            first_name='View',
            last_name='Test',
        )

    def test_register_get(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_get(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_valid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'view@example.com',
            'password': 'SecurePass123!',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_login_post_invalid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'view@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, reverse('accounts:login') + '?next=' + reverse('accounts:profile'))

    def test_profile_authenticated(self):
        self.client.login(username='view@example.com', password='SecurePass123!')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_logout_post(self):
        self.client.login(username='view@example.com', password='SecurePass123!')
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
