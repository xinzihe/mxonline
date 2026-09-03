# -*- coding: utf-8 -*-
__author__ = 'bobby'

import re
from django import forms

from operation.models import UserAsk


class UserAskForm(forms.ModelForm):
    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self):
        """
        验证手机号码是否合法
        """
        # 2. 使用 .get() 避免 KeyError，避免 mobile 为 None
        mobile = self.cleaned_data.get('mobile', '')

        # 3. 替换为兼容所有国内主流号段（13x~19x）的最新正则表达式
        REGEX_MOBILE = r"^1[3-9]\d{9}$"
        p = re.compile(REGEX_MOBILE)

        if p.match(mobile):
            return mobile
        else:
            # 4. 去掉 Python 2 遗留的 u'' 前缀
            raise forms.ValidationError("手机号码非法", code="mobile_invalid")
    # def clean_mobile(self):
    #     """
    #     验证手机号码是否合法
    #     """
    #     mobile = self.cleaned_data['mobile']
    #     REGEX_MOBILE = r"^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
    #     p = re.compile(REGEX_MOBILE)
    #     if p.match(mobile):
    #         return mobile
    #     else:
    #         raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")
