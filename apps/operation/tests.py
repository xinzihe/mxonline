from django.test import SimpleTestCase
from django.urls import reverse


class RootUrlTests(SimpleTestCase):
    def test_root_url_is_reversible(self):
        self.assertEqual(reverse('index'), '/')
