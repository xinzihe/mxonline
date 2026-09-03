# -*- coding: utf-8 -*-
__author__ = 'bobby'

from django.urls.conf import path

from .views import CourseListView, CourseDetailView, CourseInfoView, CommentsView, AddComentsView, VideoPlayView

app_name = "courses"

urlpatterns = [
    # 课程列表页
    path('list/', CourseListView.as_view(), name="course_list"),

    # 课程详情页
    path('detail/<int:course_id>/', CourseDetailView.as_view(), name="course_detail"),

    # 课程章节信息页
    path('info/<int:course_id>/', CourseInfoView.as_view(), name="course_info"),

    # 课程评论页
    path('comment/<int:course_id>/', CommentsView.as_view(), name="course_comments"),

    # 添加课程评论
    path('add_comment/', AddComentsView.as_view(), name="add_comment"),

    # 课程视频
    path('video/<int:video_id>/', VideoPlayView.as_view(), name="video_play"),
]
