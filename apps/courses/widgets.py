#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 小鑫仔
# @File    : widgets.py
# @Time    : 2026/9/3 19:30
# courses/widgets.py
from django.forms import Widget

class CustomWangEditorWidget(Widget):
    template_name = 'widgets/wang_editor.html'  # 指定你自己项目中的模板路径

    class Media:
        # 自动引入 wangEditor v5 的 CSS 和 JS 静态资源
        css = {
            'all': ('https://unpkg.com/@wangeditor/editor@latest/dist/css/style.css',)
        }
        js = (
            'https://unpkg.com/@wangeditor/editor@latest/dist/index.js',
        )