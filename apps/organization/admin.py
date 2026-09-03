from django.contrib import admin

# Register your models here.
from organization.models import CityDict, CourseOrg, Teacher


class CityDictAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'add_time')



class CourseOrgAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'tag', 'image', 'category', 'add_time')


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'org', 'image', 'add_time')


admin.site.register(CityDict, CityDictAdmin)
admin.site.register(CourseOrg, CourseOrgAdmin)
admin.site.register(Teacher, TeacherAdmin)
