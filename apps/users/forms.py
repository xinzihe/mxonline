# -*- coding: utf-8 -*-
__author__ = 'bobby'
__date__ = '2016/10/29 23:01'

from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=6, max_length=20)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=UserProfile.PASSWORD_MIN_LENGTH,
                                max_length=UserProfile.PASSWORD_MAX_LENGTH,
                                error_messages={'required': '请输入新密码。', 'min_length': '密码长度不能少于 6 位字符。',
                                                'max_length': '密码长度不能超过 20 位字符。'})
    password2 = forms.CharField(required=True, min_length=UserProfile.PASSWORD_MIN_LENGTH,
                                max_length=UserProfile.PASSWORD_MAX_LENGTH,
                                error_messages={'required': '请再次输入新密码。', 'min_length': '密码长度不能少于 6 位字符。',
                                                'max_length': '密码长度不能超过 20 位字符。'})

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') and cleaned_data.get('password2') and cleaned_data['password1'] != cleaned_data['password2']:
            raise forms.ValidationError('两次输入的密码不一致。', code='password_mismatch')
        return cleaned_data


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # 性别和生日已不在个人资料页编辑，不能继续触发表单必填校验。
        fields = ['nick_name', 'mobile']
