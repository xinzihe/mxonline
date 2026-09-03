from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_userprofile_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailverifyrecord',
            name='used_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='使用时间'),
        ),
    ]
