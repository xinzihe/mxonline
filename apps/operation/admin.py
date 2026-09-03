from django.contrib import admin

# Register your models here.
from operation.models import UserAsk, CourseComments, UserFavorite, UserMessages, UserCourse


class UserAskAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'course_name', 'add_time')


class CourseCommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'comments', 'add_time')


class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'fav_type', 'add_time')


class UserMessagesAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'has_read', 'add_time')


class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'add_time')


admin.site.register(UserAsk, UserAskAdmin)
admin.site.register(CourseComments, CourseCommentsAdmin)
admin.site.register(UserFavorite, UserFavoriteAdmin)
admin.site.register(UserMessages, UserMessagesAdmin)
admin.site.register(UserCourse, UserCourseAdmin)
