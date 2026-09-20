from django.contrib import admin

# Register your models here.
from courses.models import Course, Lesson, Video, CourseResource
from courses.widgets import CustomWangEditorWidget

#
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('course_org', 'name', 'degree', 'image', 'category', 'add_time')


class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', 'name', 'add_time')


class VideoAdmin(admin.ModelAdmin):
    list_display = ('name', 'learn_times', 'url', 'add_time')
    readonly_fields = ('learn_times',)


class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'download', 'add_time')


# admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(CourseResource, CourseResourceAdmin)
from django.db import models


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # 列表页展示的字段
    list_display = ['course_org', 'name', 'degree', 'image', 'category', 'add_time']

    # 列表页允许点击进入编辑页的字段（默认是第一个字段）
    # list_display_links = ['name']

    # 列表页侧边栏筛选器（可选）
    # list_filter = ['degree', 'category', 'add_time']

    # 列表页搜索框可搜索的字段（可选）
    # search_fields = ['name', 'category']

    # 表单新增/编辑页中的 TextField 使用富文本编辑器渲染
    formfield_overrides = {
        models.TextField: {'widget': CustomWangEditorWidget},
    }
