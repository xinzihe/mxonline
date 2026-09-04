import json

from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls.base import reverse
from django.views.generic.base import View
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from courses.models import Course
from organization.models import CourseOrg, Teacher
from django.db.models import Count, Sum
from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from users.models import UserProfile, EmailVerifyRecord, Banner
from operation.models import UserCourse, UserFavorite, UserMessages
from utils.email_send import send_register_email, EmailRateLimitError
from utils.mixin_utils import LoginRequiredMixin


# Create your views here.
class CustomBackend(ModelBackend):
    # 必须加上 request 参数
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 支持用户名或邮箱登录
            # user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            user = UserProfile.objects.get(username=username)
            # 校验密码，并确保用户处于激活状态 (is_active=True)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserProfile.DoesNotExist:
            return None
        return None


class ActiveUserView(View):
    def get(self, request, active_code):
        record = EmailVerifyRecord.objects.filter(code=active_code, send_type='register').order_by('-send_time').first()
        if not record or not record.is_valid(settings.EMAIL_VERIFY_TTL_MINUTES):
            return render(request, "active_fail.html")
        user = UserProfile.objects.filter(email=record.email).first()
        if not user:
            return render(request, "active_fail.html")
        user.is_active = True
        user.save(update_fields=['is_active'])
        record.used_at = timezone.now()
        record.save(update_fields=['used_at'])
        return render(request, "login.html")


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户已经存在"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessages()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册慕学在线网"
            user_message.save()

            try:
                send_register_email(user_name, "register")
            except EmailRateLimitError as exc:
                return render(request, "register.html", {"register_form": register_form, "msg": str(exc)})
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


class LogoutView(View):
    """
    用户登出
    """

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg": "用户未激活！"})
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误！"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form": forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            if UserProfile.objects.filter(email=email).exists():
                try:
                    send_register_email(email, "forget")
                except EmailRateLimitError as exc:
                    return render(request, "forgetpwd.html", {"forget_form": forget_form, "msg": str(exc)})
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})


class ResetView(View):
    def get(self, request, active_code):
        record = EmailVerifyRecord.objects.filter(code=active_code, send_type='forget').order_by('-send_time').first()
        if not record or not record.is_valid(settings.EMAIL_VERIFY_TTL_MINUTES):
            return render(request, "active_fail.html")
        return render(request, "password_reset.html", {"reset_code": record.code})


class ModifyPwdView(View):
    """
    修改用户密码
    """

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            reset_code = request.POST.get("reset_code", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"reset_code": reset_code, "msg": "密码不一致"})
            record = EmailVerifyRecord.objects.filter(code=reset_code, send_type='forget').order_by('-send_time').first()
            if not record or not record.is_valid(settings.EMAIL_VERIFY_TTL_MINUTES):
                return render(request, "active_fail.html")
            user = UserProfile.objects.filter(email=record.email).first()
            if not user:
                return render(request, "active_fail.html")
            user.password = make_password(pwd2)
            user.save(update_fields=['password'])
            record.used_at = timezone.now()
            record.save(update_fields=['used_at'])

            return render(request, "login.html")
        else:
            return render(request, "password_reset.html", {
                "reset_code": request.POST.get("reset_code", ""),
                "modify_form": modify_form,
                "msg": ' '.join(error for errors in modify_form.errors.values() for error in errors),
            })


class UserinfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """

    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """

    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    """
    个人中心修改用户密码
    """

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}', content_type='application/json')
            user = request.user
            user.set_password(pwd2)
            user.save(update_fields=['password'])
            update_session_auth_hash(request, user)

            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """

    def get(self, request):
        email = request.GET.get('email', '')

        try:
            validate_email(email)
        except ValidationError:
            return HttpResponse('{"email":"邮箱格式错误"}', content_type='application/json')
        if UserProfile.objects.exclude(pk=request.user.pk).filter(email=email).exists():
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
        try:
            send_register_email(email, "update_email")
        except EmailRateLimitError as exc:
            return HttpResponse(json.dumps({"email": str(exc)}), content_type='application/json')

        return HttpResponse('{"status":"success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """
    修改个人邮箱
    """

    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        record = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email').order_by('-send_time').first()
        if record and record.is_valid(settings.EMAIL_VERIFY_TTL_MINUTES):
            user = request.user
            user.email = email
            user.save(update_fields=['email'])
            record.used_at = timezone.now()
            record.save(update_fields=['used_at'])
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """
    我的课程
    """

    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {
            "user_courses": user_courses
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    我收藏的课程机构
    """

    def get(self, request):
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        org_list = CourseOrg.objects.filter(id__in=fav_orgs.values_list('fav_id', flat=True))
        return render(request, 'usercenter-fav-org.html', {
            "org_list": org_list
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    我收藏的授课讲师
    """

    def get(self, request):
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        teacher_list = Teacher.objects.filter(id__in=fav_teachers.values_list('fav_id', flat=True))
        return render(request, 'usercenter-fav-teacher.html', {
            "teacher_list": teacher_list
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    我收藏的课程
    """

    def get(self, request):
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        course_list = Course.objects.filter(id__in=fav_courses.values_list('fav_id', flat=True))
        return render(request, 'usercenter-fav-course.html', {
            "course_list": course_list
        })


class MymessageView(LoginRequiredMixin, View):
    """
    我的消息
    """

    def get(self, request):
        all_messages = UserMessages.objects.filter(user=request.user.id)
        all_messages = all_messages.order_by('-add_time')

        # 用户进入个人消息后清空未读消息的记录
        all_unread_messages = UserMessages.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息进行分页
        p = Paginator(all_messages, 10, request=request)
        try:
            messages = p.page(request.GET.get('page', 1))
        except (PageNotAnInteger, EmptyPage):
            messages = p.page(1)
        return render(request, 'usercenter-message.html', {
            "messages": messages
        })


class IndexView(View):
    # 慕学在线网 首页
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        # 首页平台概览统一从数据库聚合，避免模板或视图写死统计数字。
        course_stats = Course.objects.aggregate(
            course_count=Count('id'),
            student_count=Sum('students'),
        )
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
            'course_count': course_stats['course_count'],
            'org_count': CourseOrg.objects.count(),
            'student_count': course_stats['student_count'] or 0,
        })


def page_not_found(request, exception=None):
    # 全局 404 处理函数
    return render(request, '404.html', status=404)


def page_error(request):
    # 全局 500 处理函数
    return render(request, '500.html', status=500)

# def page_not_found(request):
#     # 全局404处理函数
#     from django.shortcuts import render_to_response
#     response = render_to_response('404.html', {})
#     response.status_code = 404
#     return response
#
#
# def page_error(request):
#     # 全局500处理函数
#     from django.shortcuts import render_to_response
#     response = render_to_response('500.html', {})
#     response.status_code = 500
#     return response
