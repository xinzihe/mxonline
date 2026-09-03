# 知行在线

这是一个基于 Django 的在线课程平台，包含用户、课程、机构、讲师、收藏和学习记录功能。

## 本地配置

在 PowerShell 中先设置环境变量（请使用自己新生成的密钥和 SMTP 授权码）：

```powershell
$env:DJANGO_SECRET_KEY = 'replace-with-a-long-random-secret'
$env:DJANGO_DEBUG = 'true'
$env:MYSQL_PASSWORD = 'your-mysql-password'
$env:EMAIL_HOST_USER = 'your-smtp-account@example.com'
$env:EMAIL_HOST_PASSWORD = 'your-smtp-app-password'
```

完整变量清单见 `.env.example`。生产环境还必须设置 `DJANGO_DEBUG=false`、`DJANGO_ALLOWED_HOSTS` 和 HTTPS 相关配置。

安装依赖、执行迁移并启动：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

`staticfiles/` 是 `collectstatic` 输出目录，部署时重新生成，不作为手工维护的源文件。
