from django.contrib import admin

# Register your models here.

from users.models import UserProfile, EmailVerifyRecord, Banner


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "sex", "mobile", "is_active", "date_joined", "last_login")


class EmailVerifyRecordAdmin(admin.ModelAdmin):
    list_display = ('code', 'email', 'send_type', 'send_time')


class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'url', 'index', 'add_time')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
admin.site.register(Banner, BannerAdmin)
