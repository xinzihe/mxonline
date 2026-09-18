from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.urls import reverse
from pure_pagination import Paginator


class OrganizationUrlTests(SimpleTestCase):
    def test_organization_urls_are_reversible(self):
        self.assertEqual(reverse('org:org_list'), '/org/list/')
        self.assertEqual(reverse('org:teacher_detail', args=[1]), '/org/teacher/detail/1/')

    def test_org_list_renders_when_filter_has_no_results(self):
        request = RequestFactory().get('/org/list/?city=4&ct=gx')
        request.user = AnonymousUser()
        empty_page = Paginator([], 5, request=request).page(1)

        html = render_to_string('org-list.html', {
            'all_orgs': empty_page,
            'all_cities': [],
            'org_categories': [('pxjg', '培训机构'), ('gr', '个人'), ('gx', '高校')],
            'org_nums': 0,
            'city_id': '4',
            'category': 'gx',
            'hot_orgs': [],
            'sort': '',
        }, request=request)

        self.assertIn('未找到符合条件的授课机构', html)

    def test_teacher_list_renders_when_no_teachers_exist(self):
        request = RequestFactory().get('/org/teacher/list/')
        request.user = AnonymousUser()
        empty_page = Paginator([], 10, request=request).page(1)

        html = render_to_string('teachers-list.html', {
            'all_teachers': empty_page,
            'teacher_nums': 0,
            'sorted_teachers': [],
            'sort': '',
            'fav_teacher_ids': set(),
        }, request=request)

        self.assertIn('暂无入驻讲师', html)
