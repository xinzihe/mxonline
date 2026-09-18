from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.urls import reverse
from pure_pagination import Paginator


class CourseUrlTests(SimpleTestCase):
    def test_course_urls_are_reversible(self):
        self.assertEqual(reverse('course:course_list'), '/course/list/')
        self.assertEqual(reverse('course:course_detail', args=[1]), '/course/detail/1/')
        self.assertEqual(reverse('course:video_play', args=[1]), '/course/video/1/')

    def test_course_list_renders_when_no_courses_exist(self):
        request = RequestFactory().get('/course/list/')
        request.user = AnonymousUser()
        empty_page = Paginator([], 12, request=request).page(1)

        html = render_to_string('course-list.html', {
            'all_courses': empty_page,
            'course_nums': 0,
            'hot_courses': [],
            'sort': '',
            'category': '',
            'degree': '',
            'keywords': '',
        }, request=request)

        self.assertIn('未找到符合条件的课程', html)
