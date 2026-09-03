from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='userfavorite',
            constraint=models.UniqueConstraint(fields=('user', 'fav_id', 'fav_type'), name='unique_user_favorite'),
        ),
        migrations.AddConstraint(
            model_name='usercourse',
            constraint=models.UniqueConstraint(fields=('user', 'course'), name='unique_user_course'),
        ),
    ]
