from django.test import SimpleTestCase
from django.urls import reverse


class UserUrlTests(SimpleTestCase):
    def test_user_urls_are_reversible(self):
        self.assertEqual(reverse('login'), '/login/')
        self.assertEqual(reverse('users:image_upload'), '/users/image/upload/')
        self.assertEqual(reverse('users:mymessage'), '/users/mymessage/')
