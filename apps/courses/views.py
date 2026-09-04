from django.db.models import F
from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View

from courses.models import Course, CourseResource, Video
from operation.models import UserCourse, UserFavorite, CourseComments
from utils.mixin_utils import LoginRequiredMixin
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by("-add_time")

        hot_courses = Course.objects.all().order_by("-click_nums")[:3]

        # 课程搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                    detail__icontains=search_keywords))

        category = request.GET.get('category', '')
        if category:
            all_courses = all_courses.filter(category=category)

        degree = request.GET.get('degree', '')
        if degree in {'cj', 'zj', 'gj'}:
            all_courses = all_courses.filter(degree=degree)

        # 课程排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_courses = all_courses.order_by("-students")
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")

        # 对课程进行分页
        p = Paginator(all_courses, 12, request=request)
        try:
            courses = p.page(request.GET.get('page', 1))
        except (PageNotAnInteger, EmptyPage):
            courses = p.page(1)

        return render(request, 'course-list.html', {
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses,
            "category": category,
            "degree": degree,
            "keywords": search_keywords,
        })


class CourseDetailView(View):
    """
    课程详情页
    """

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # 增加课程点击数
        course.click_nums += 1
        course.save()

        # 是否收藏课程
        has_fav_course = False
        # 是否收藏机构
        has_fav_org = False

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True

            if course.course_org and UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 相关推荐
        tag = course.tag
        if tag:
            relate_coures = Course.objects.filter(tag=tag)[:1]
        else:
            relate_coures = []
        return render(request, "course-detail.html", {
            "course": course,
            "relate_coures": relate_coures,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        # 仅在首次学习时建立关系并增加人数，避免刷新页面导致统计失真。
        _, created = UserCourse.objects.get_or_create(user=request.user, course=course)
        if created:
            Course.objects.filter(pk=course.pk).update(students=F('students') + 1)
            course.refresh_from_db(fields=['students'])

        user_cousers = UserCourse.objects.filter(course=course)
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_couser.course.id for user_couser in all_user_courses]
        # 获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course).select_related('user').order_by("-id")
        # 学习页直接嵌入播放器，首次进入时默认选中课程的第一节视频，但不自动播放。
        current_video = Video.objects.filter(
            lesson__course=course
        ).select_related("lesson").order_by("lesson_id", "id").first()
        return render(request, "course-video.html", {
            "course": course,
            "video": current_video,
            "course_resources": all_resources,
            "relate_courses": relate_courses,
            "all_comments": all_comments,
        })


class CommentsView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course).select_related('user').order_by("-id")
        return render(request, "course-comment.html", {
            "course": course,
            "course_resources": all_resources,
            "all_comments": all_comments

        })


class AddComentsView(View):
    """
    用户添加课程评论
    """

    def post(self, request):
        if not request.user.is_authenticated:
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        # 安全地将 course_id 转换为整数，若转换失败则默认为 0
        try:
            course_id = int(request.POST.get("course_id", 0))
        except (ValueError, TypeError):
            course_id = 0
        # course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        if course_id > 0 and comments:
            try:
                course = Course.objects.get(id=course_id)
                course_comments = CourseComments()
                course_comments.course = course
                course_comments.comments = comments
                course_comments.user = request.user
                course_comments.save()
                return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
            except Course.DoesNotExist:
                return HttpResponse('{"status":"fail", "msg":"课程不存在"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')
        # if course_id > 0 and comments:
        #     course_comments = CourseComments()
        #     course = Course.objects.get(id=int(course_id))
        #     course_comments.course = course
        #     course_comments.comments = comments
        #     course_comments.user = request.user
        #     course_comments.save()
        #     return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        # else:
        #     return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')





class VideoPlayView(LoginRequiredMixin, View):
    """
    课程视频播放视图
    """

    def get(self, request, video_id):
        # 1. 根据视频 ID 获取视频对象（不存在则抛出 404）
        video = get_object_or_404(Video, id=int(video_id))

        # 2. 获取该视频所属的课程
        if not video.lesson or not video.lesson.course:
            return HttpResponse('视频未关联课程', status=404)
        course = video.lesson.course
        if not UserCourse.objects.filter(user=request.user, course=course).exists():
            return HttpResponse('请先从课程详情页开始学习', status=403)

        # 3. 视频播放复用课程学习页，不再打开一套独立且容易样式冲突的页面。
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course).select_related('user').order_by("-id")

        # 4. 渲染统一学习页面，并将用户点击的视频作为当前播放项。
        return render(request, "course-video.html", {
            "course": course,
            "video": video,
            "course_resources": all_resources,
            "relate_courses": [],
            "all_comments": all_comments,
        })
