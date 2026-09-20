from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.urls import reverse
from pure_pagination import Paginator
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from courses.models import Lesson, Video
from courses.video_duration import VideoDurationError, get_video_duration_minutes


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
            'course_categories': ['后端开发'],
            'course_degrees': [('cj', '初级')],
        }, request=request)

        self.assertIn('未找到符合条件的课程', html)
        self.assertIn('后端开发', html)
        self.assertIn('初级', html)


class VideoDurationTests(SimpleTestCase):
    @patch('courses.video_duration.subprocess.run')
    def test_duration_is_rounded_up_to_whole_minutes(self, run):
        run.return_value = Mock(returncode=0, stdout='61.1\n')

        self.assertEqual(get_video_duration_minutes('lesson.mp4'), 2)

    @patch('courses.video_duration.subprocess.run')
    def test_invalid_video_duration_raises_clear_error(self, run):
        run.return_value = Mock(returncode=0, stdout='N/A\n')

        with self.assertRaises(VideoDurationError):
            get_video_duration_minutes('not-a-video.txt')


class VideoModelTests(TestCase):
    @patch('courses.models.get_video_duration_minutes', return_value=3)
    def test_uploading_a_new_video_updates_its_duration(self, duration):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            lesson = Lesson.objects.create(name='第一章')
            video = Video.objects.create(
                lesson=lesson,
                name='课程导学',
                url=SimpleUploadedFile('intro.mp4', b'video-content'),
            )

            video.refresh_from_db()

        self.assertEqual(video.learn_times, 3)
        duration.assert_called_once()
