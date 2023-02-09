# Generated by Django 4.1.6 on 2023-02-09 00:20

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_follows'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=150, validators=[users.validators.NameValidator()], verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150, validators=[users.validators.NameValidator()], verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'That username is already in use'}, help_text='Required. 3 to 63 characters. Letters, digits and underscore only.', max_length=150, unique=True, validators=[users.validators.UsernameValidator()], verbose_name='username'),
        ),
    ]
