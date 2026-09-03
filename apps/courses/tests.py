from django.test import SimpleTestCase
from django.urls import reverse


class CourseUrlTests(SimpleTestCase):
    def test_course_urls_are_reversible(self):
        self.assertEqual(reverse('course:course_list'), '/course/list/')
        self.assertEqual(reverse('course:course_detail', args=[1]), '/course/detail/1/')
        self.assertEqual(reverse('course:video_play', args=[1]), '/course/video/1/')
