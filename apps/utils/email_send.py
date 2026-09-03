# -*- coding: utf-8 -*-
__author__ = 'bobby'
__date__ = '2016/10/30 22:11'

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from users.models import EmailVerifyRecord

# 原有
# def random_str(randomlength=8):
#     str = ''
#     chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
#     length = len(chars) - 1
#     random = Random()
#     for i in range(randomlength):
#         str+=chars[random.randint(0, length)]
#     return str


# 优化
import secrets
import string


def random_str(randomlength=8):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(randomlength))


class EmailRateLimitError(Exception):
    pass


def send_register_email(email, send_type="register"):
    if send_type not in {'register', 'forget', 'update_email'}:
        raise ValueError('Unsupported email verification type.')
    recent_record = EmailVerifyRecord.objects.filter(
        email=email, send_type=send_type, send_time__gte=timezone.now() - timedelta(seconds=60),
    ).exists()
    if recent_record:
        raise EmailRateLimitError('请在 60 秒后再试。')
    email_record = EmailVerifyRecord()
    if send_type == "update_email":
        code = random_str(4)
    else:
        code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "慕学在线网注册激活链接"
        email_body = f"请点击下面的链接激活你的账号: {settings.SITE_URL}/active/{code}/"

        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "forget":
        email_title = "慕学在线网注册密码重置链接"
        email_body = f"请点击下面的链接重置密码: {settings.SITE_URL}/reset/{code}/"

        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "update_email":
        email_title = "慕学在线邮箱修改验证码"
        email_body = f"你的邮箱验证码为: {code}"

        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if send_status:
            pass
