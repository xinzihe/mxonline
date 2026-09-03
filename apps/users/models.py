from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50, verbose_name="昵称", default="")
    birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    sex = models.CharField(max_length=6, choices=(("male", "男"), ("female", "女")), default="male")
    address = models.CharField(max_length=100, default="")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(max_length=100, upload_to="images/%Y/%m", default="images/default.jpg")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def unread_nums(self):
        #获取用户未读消息的数量
        from operation.models import UserMessages
        return UserMessages.objects.filter(user=self.id, has_read=False).count()



class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name="验证码")
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    send_type = models.CharField(max_length=20,
                                 choices=(("register", "注册"), ("forget", "忘记"), ("update_email", "修改邮箱")))
    send_time = models.DateTimeField(default=datetime.now, verbose_name="发送时间")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="使用时间")

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name

    def is_valid(self, ttl_minutes):
        from django.utils import timezone
        from datetime import timedelta
        return self.used_at is None and self.send_time >= timezone.now() - timedelta(minutes=ttl_minutes)


class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name="标题")
    image = models.ImageField(max_length=100, upload_to="banner/%Y/%m", verbose_name="轮播图")
    url = models.URLField(max_length=200, verbose_name="访问地址")
    index = models.IntegerField(default=100, verbose_name="顺序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "轮播图"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
