# Generated by Django 4.1.6 on 2023-02-09 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_first_name_alter_user_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(default='profile_pics/default.jpeg', upload_to='profile_pics/%Y/%m/%d', verbose_name='Profile Picture'),
        ),
    ]
