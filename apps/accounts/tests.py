"""Unit tests for accounts app: registration, login, logout, onboarding and plan flows."""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch

from apps.core.models import PlanAEnrollment, PlanBEnrollment

STATIC_OVERRIDE = override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'
)


@STATIC_OVERRIDE
class RegisterViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:register')

    def test_get_renders_register_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertIn('form', response.context)

    def test_authenticated_user_redirected_from_register(self):
        user = User.objects.create_user(username='existing', password='pass1234')
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:dashboard'))

    @patch('apps.accounts.views._send_plan_a_credentials_email', return_value=True)
    def test_valid_registration_creates_user_and_enrollment(self, mock_email):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('accounts:plan_a_onboarding'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        enrollment = PlanAEnrollment.objects.get(user=user)
        self.assertEqual(enrollment.status, 'active')
        self.assertIsNotNone(enrollment.purchased_at)
        self.assertIsNotNone(enrollment.first_login_at)
        self.assertIsNotNone(enrollment.credentials_email_sent_at)

    def test_invalid_registration_passwords_dont_match(self):
        data = {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password': 'pass1234',
            'password_confirm': 'different',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='baduser').exists())

    def test_invalid_registration_duplicate_username(self):
        User.objects.create_user(username='taken', password='pass')
        data = {
            'username': 'taken',
            'email': 'x@x.com',
            'password': 'pass1234',
            'password_confirm': 'pass1234',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='taken').count(), 1)

    @patch('apps.accounts.views._send_plan_a_credentials_email', side_effect=Exception('SMTP error'))
    def test_registration_continues_even_when_email_fails(self, mock_email):
        data = {
            'username': 'emailfail',
            'email': 'fail@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('accounts:plan_a_onboarding'))
        self.assertTrue(User.objects.filter(username='emailfail').exists())


@STATIC_OVERRIDE
class LoginViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='testuser', password='testpass', email='test@example.com'
        )

    def test_get_renders_login_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_authenticated_user_redirected_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'testpass',
        })
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('incorrectos' in str(m) for m in messages))

    def test_login_sets_first_login_at_on_enrollment(self):
        enrollment = PlanAEnrollment.objects.create(user=self.user)
        self.assertIsNone(enrollment.first_login_at)
        self.client.post(self.url, {'username': 'testuser', 'password': 'testpass'})
        enrollment.refresh_from_db()
        self.assertIsNotNone(enrollment.first_login_at)

    def test_login_does_not_overwrite_first_login_at(self):
        ts = timezone.now()
        enrollment = PlanAEnrollment.objects.create(user=self.user, first_login_at=ts)
        self.client.post(self.url, {'username': 'testuser', 'password': 'testpass'})
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.first_login_at, ts)

    def test_login_respects_next_param(self):
        target = reverse('accounts:account_settings')
        response = self.client.post(f'{self.url}?next={target}', {
            'username': 'testuser',
            'password': 'testpass',
        })
        self.assertRedirects(response, target)


@STATIC_OVERRIDE
class LogoutViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='logoutuser', password='pass')
        self.url = reverse('accounts:logout')

    def test_logout_post_redirects_to_home(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('home'))

    def test_logout_terminates_session(self):
        self.client.force_login(self.user)
        self.client.post(self.url)
        dashboard = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(dashboard, f"{reverse('accounts:login')}?next={reverse('core:dashboard')}")


@STATIC_OVERRIDE
class PlanAOnboardingViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='planuser', password='pass', email='p@p.com')
        self.client.force_login(self.user)
        self.url = reverse('accounts:plan_a_onboarding')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    @patch('apps.accounts.views._send_plan_a_credentials_email', return_value=True)
    def test_get_activates_enrollment_and_renders(self, mock_email):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/plan_a_onboarding.html')
        enrollment = PlanAEnrollment.objects.get(user=self.user)
        self.assertEqual(enrollment.status, 'active')

    @patch('apps.accounts.views._send_plan_a_credentials_email', return_value=True)
    def test_step_flags_in_context(self, mock_email):
        response = self.client.get(self.url)
        ctx = response.context
        # step1 depends on credentials_email_sent_at being set
        self.assertIn('step1_done', ctx)
        self.assertIn('step2_done', ctx)
        self.assertIn('step3_done', ctx)


@STATIC_OVERRIDE
class AccountSettingsViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='settingsuser', password='pass')
        self.client.force_login(self.user)
        self.url = reverse('accounts:account_settings')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_renders_account_settings(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/account_settings.html')

    def test_context_includes_plan_data(self):
        PlanAEnrollment.objects.create(user=self.user, status='active')
        response = self.client.get(self.url)
        self.assertIn('plan_a', response.context)
        self.assertIn('plan_b', response.context)
