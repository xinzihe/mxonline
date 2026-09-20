from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import EmailVerifyRecord, UserProfile
from users.views import CustomBackend


class UserUrlTests(SimpleTestCase):
    def test_user_urls_are_reversible(self):
        self.assertEqual(reverse('login'), '/login/')
        self.assertEqual(reverse('users:image_upload'), '/users/image/upload/')
        self.assertEqual(reverse('users:mymessage'), '/users/mymessage/')


class CaptchaRefreshTests(TestCase):
    def test_register_page_loads_captcha_refresh_script(self):
        response = self.client.get(reverse('register'))

        self.assertContains(response, '/static/js/captcha-refresh.js')

    def test_captcha_refresh_returns_new_key_and_image_url(self):
        response = self.client.get(
            reverse('captcha-refresh'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('key', response.json())
        self.assertIn('image_url', response.json())


class ActivationAndLoginTests(TestCase):
    def test_activation_page_explains_how_to_log_in(self):
        user = UserProfile.objects.create_user(
            username='student@example.com', email='student@example.com',
            password='secret123', is_active=False,
        )
        record = EmailVerifyRecord.objects.create(
            code='activate-user', email=user.email, send_type='register',
            send_time=timezone.now(),
        )

        response = self.client.get(reverse('user_active', args=[record.code]))

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertContains(response, '请使用注册邮箱和密码登录')

    def test_login_backend_authenticates_with_email(self):
        user = UserProfile.objects.create_user(
            username='legacy_user', email='legacy@example.com', password='secret123',
        )

        authenticated_user = CustomBackend().authenticate(
            None, email='legacy@example.com', password='secret123',
        )

        self.assertEqual(authenticated_user, user)

    def test_login_view_accepts_email_field(self):
        UserProfile.objects.create_user(
            username='student@example.com', email='student@example.com', password='secret123',
        )

        response = self.client.post(reverse('login'), {
            'email': 'student@example.com', 'password': 'secret123',
        })

        self.assertRedirects(response, reverse('index'))
