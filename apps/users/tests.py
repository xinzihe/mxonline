from django.test import SimpleTestCase, TestCase
from django.urls import reverse


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
