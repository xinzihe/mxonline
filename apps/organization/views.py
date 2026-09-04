from pure_pagination import PageNotAnInteger, Paginator, EmptyPage
from django.db.models.query_utils import Q
from django.db import transaction
from django.db.models import F
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View

from courses.models import Course
from operation.models import UserFavorite
from organization.forms import UserAskForm
from organization.models import CourseOrg, CityDict, Teacher


# Create your views here.


class OrgView(View):
    """
    课程机构列表功能
    """

    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        hot_orgs = all_orgs.order_by("-click_nums")[:3]

        # 城市
        all_citys = CityDict.objects.all()

        # 机构搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        # 取出筛选城市
        city_id = request.GET.get('city', "")
        if city_id:
            try:
                all_orgs = all_orgs.filter(city_id=int(city_id))
            except (TypeError, ValueError):
                city_id = ''

        # 类别筛选
        category = request.GET.get('ct', "")
        if category:
            all_orgs = all_orgs.filter(category=category)

        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        org_nums = all_orgs.count()

        # 对课程机构进行分页
        p = Paginator(all_orgs, 5, request=request)
        try:
            orgs = p.page(request.GET.get('page', 1))
        except (PageNotAnInteger, EmptyPage):
            orgs = p.page(1)
        return render(request, "org-list.html", {
            "all_orgs": orgs,
            "all_citys": all_citys,
            "org_nums": org_nums,
            "city_id": city_id,
            "category": category,
            "hot_orgs": hot_orgs,
            "sort": sort
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """

    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """

    def get(self, request, org_id):
        current_page = "home"
        course_org = get_object_or_404(CourseOrg, id=org_id)
        # 使用数据库原子更新，避免并发访问时丢失机构点击数。
        CourseOrg.objects.filter(pk=course_org.pk).update(click_nums=F('click_nums') + 1)
        course_org.refresh_from_db(fields=['click_nums'])
        has_fav = False
        if request.user.is_authenticated:
            has_fav = UserFavorite.objects.filter(
                user=request.user, fav_id=course_org.id, fav_type=2,
            ).exists()

        all_courses = course_org.course_set.select_related('teacher').order_by('-click_nums', '-add_time')[:3]
        all_teachers = course_org.teacher_set.all().order_by('-click_nums', '-add_time')[:3]
        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        })


class OrgCourseView(View):
    """
    机构课程列表页
    """

    def get(self, request, org_id):
        current_page = "course"
        course_org = get_object_or_404(CourseOrg, id=org_id)
        has_fav = False
        if request.user.is_authenticated:
            has_fav = UserFavorite.objects.filter(
                user=request.user, fav_id=course_org.id, fav_type=2,
            ).exists()
        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        })


class OrgDescView(View):
    """
    机构介绍页
    """

    def get(self, request, org_id):
        current_page = "desc"
        course_org = get_object_or_404(CourseOrg, id=org_id)
        has_fav = False
        if request.user.is_authenticated:
            has_fav = UserFavorite.objects.filter(
                user=request.user, fav_id=course_org.id, fav_type=2,
            ).exists()
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        })


class OrgTeacherView(View):
    """
    机构教师页
    """

    def get(self, request, org_id):
        current_page = "teacher"
        course_org = get_object_or_404(CourseOrg, id=org_id)
        has_fav = False
        if request.user.is_authenticated:
            has_fav = UserFavorite.objects.filter(
                user=request.user, fav_id=course_org.id, fav_type=2,
            ).exists()
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav

        })


class AddFavView(View):
    """
    用户收藏，用户取消收藏
    """

    def post(self, request):
        if not request.user.is_authenticated:
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        try:
            fav_id = int(request.POST.get('fav_id', 0))
            fav_type = int(request.POST.get('fav_type', 0))
        except (TypeError, ValueError):
            return HttpResponse('{"status":"fail", "msg":"关注参数错误"}', content_type='application/json')
        model_by_type = {1: Course, 2: CourseOrg, 3: Teacher}
        model = model_by_type.get(fav_type)
        if not model or fav_id <= 0:
            return HttpResponse('{"status":"fail", "msg":"关注参数错误"}', content_type='application/json')

        with transaction.atomic():
            target = get_object_or_404(model, pk=fav_id)
            favorite, created = UserFavorite.objects.get_or_create(
                user=request.user, fav_id=fav_id, fav_type=fav_type,
            )
            follow_label_by_type = {1: '关注课程', 2: '关注机构', 3: '关注讲师'}
            if created:
                model.objects.filter(pk=target.pk).update(fav_nums=F('fav_nums') + 1)
                action = 'followed'
                button_label = '取消关注'
            else:
                favorite.delete()
                model.objects.filter(pk=target.pk, fav_nums__gt=0).update(fav_nums=F('fav_nums') - 1)
                action = 'unfollowed'
                button_label = follow_label_by_type[fav_type]
        return JsonResponse({
            'status': 'success',
            'action': action,
            'label': button_label,
            # 保留 msg 字段，兼容尚未改造的旧页面脚本。
            'msg': button_label,
        })


class TeacherListView(View):
    """
    课程讲师列表页
    """

    def get(self, request):
        all_teachers = Teacher.objects.all()

        # 课程讲师搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords) |
                                               Q(work_company__icontains=search_keywords) |
                                               Q(work_position__icontains=search_keywords))

        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")

        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]

        # 对讲师进行分页
        p = Paginator(all_teachers, 10, request=request)
        try:
            teachers = p.page(request.GET.get('page', 1))
        except (PageNotAnInteger, EmptyPage):
            teachers = p.page(1)
        fav_teacher_ids = set()
        if request.user.is_authenticated:
            fav_teacher_ids = set(UserFavorite.objects.filter(
                user=request.user, fav_type=3,
            ).values_list('fav_id', flat=True))
        return render(request, "teachers-list.html", {
            "all_teachers": teachers,
            "sorted_teachers": sorted_teacher,
            "sort": sort,
            "fav_teacher_ids": fav_teacher_ids,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        teacher.click_nums += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)

        has_teacher_faved = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
                has_teacher_faved = True

        has_org_faved = False
        if request.user.is_authenticated:
            if teacher.org and UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_org_faved = True

        # 讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        return render(request, "teacher-detail.html", {
            "teacher": teacher,
            "all_courses": all_courses,
            "sorted_teacher": sorted_teacher,
            "has_teacher_faved": has_teacher_faved,
            "has_org_faved": has_org_faved
        })
