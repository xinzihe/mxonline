from django.db import models
from datetime import datetime

from organization.models import CourseOrg, Teacher


# Create your models here.
#  课程
class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name="课程机构", null=True, blank=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=50, verbose_name="课程名")
    desc = models.CharField(max_length=300, verbose_name="课程描述")
    detail = models.TextField(verbose_name="课程详情")
    degree = models.CharField(max_length=2, choices=(("cj", "初级"), ("zj", "中级"), ("gj", "高级")),
                              verbose_name="课程难度")
    is_banner = models.BooleanField(default=False, verbose_name=u"是否轮播")
    teacher = models.ForeignKey(Teacher, verbose_name=u"讲师", null=True, blank=True, on_delete=models.SET_NULL)

    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟)")
    students = models.IntegerField(default=0, verbose_name="学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏人数")
    image = models.ImageField(max_length=100, upload_to="courses/%Y/%m", verbose_name="封面图")
    click_nums = models.IntegerField(default=0, verbose_name="课程点击人数")
    category = models.CharField(default=u"后端开发", max_length=20, verbose_name=u"课程类别")
    tag = models.CharField(default="", verbose_name=u"课程标签", max_length=10)
    youneed_know = models.CharField(default="", max_length=300, verbose_name=u"课程须知")
    teacher_tell = models.CharField(default="", max_length=300, verbose_name=u"老师告诉你")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_zj_nums(self):
        # 获取课程章节数
        return self.lesson_set.all().count()

    get_zj_nums.short_description = "章节数"

    def go_to(self):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='http://www.projectsedu.com'>跳转</>")

    go_to.short_description = "跳转"

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        # 获取课程所有章节
        return self.lesson_set.all()


# 章节
class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, verbose_name="章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_lesson_video(self):
        # 获取章节视频
        return self.video_set.all()


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="章节", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, verbose_name="视频名")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    url = models.FileField(max_length=500, default="", verbose_name="访问地址")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 课程资源
class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, verbose_name="名称")
    download = models.FileField(max_length=100, upload_to="course/resource/%Y/%m", verbose_name="资源文件")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
