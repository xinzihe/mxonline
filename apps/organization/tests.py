from django.test import SimpleTestCase
from django.urls import reverse


class OrganizationUrlTests(SimpleTestCase):
    def test_organization_urls_are_reversible(self):
        self.assertEqual(reverse('org:org_list'), '/org/list/')
        self.assertEqual(reverse('org:teacher_detail', args=[1]), '/org/teacher/detail/1/')
