"""
URL configuration for MxOnline project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import mimetypes
from pathlib import Path

from django.contrib import admin
from django.http.response import Http404
from django.urls import path
from django.urls.conf import include, re_path
from ranged_response import RangedFileResponse
from MxOnline import settings
from users.views import LoginView, RegisterView, ForgetPwdView, ActiveUserView, ResetView, ModifyPwdView, LogoutView, \
    IndexView


def media_serve(request, path):
    # 1. 拼接媒体文件物理路径
    media_root = Path(settings.MEDIA_ROOT).resolve()
    file_path = (media_root / path).resolve()

    # 2. 检查文件是否存在
    if media_root not in file_path.parents or not file_path.is_file():
        raise Http404("Media file does not exist")

    # 3. 自动识别视频 Content-Type (如 video/mp4)
    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or 'application/octet-stream'

    # 4. 直接打开文件流传递给 RangedFileResponse，解决拖拽与报错问题
    return RangedFileResponse(request, file_path.open('rb'), content_type=content_type)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('captcha/', include('captcha.urls')),

    # 配置上传文件的访问处理函数
    re_path(r'^media/(?P<path>.*)$', media_serve),
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name="logout"),

    path('register/', RegisterView.as_view(), name="register"),
    path('forget/', ForgetPwdView.as_view(), name="forget_pwd"),
    path('active/<str:active_code>/', ActiveUserView.as_view(), name='user_active'),
    path('reset/<str:active_code>/', ResetView.as_view(), name='reset_pwd'),
    path('modify_pwd/', ModifyPwdView.as_view(), name='modify_pwd'),

    # 课程机构url配置
    path('org/', include('organization.urls', namespace="org")),

    # 用户相关url配置
    path('users/', include('users.urls', namespace='users')),
    # 课程相关url配置
    path('course/', include('courses.urls', namespace="course")),
]
# 全局404页面配置
handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'
