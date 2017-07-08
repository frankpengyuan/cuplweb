# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-07 22:36
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=5)),
                ('course_cat', models.CharField(choices=[('pe1or3', 'PE 1 or PE 3'), ('pe2or4', 'PE 2 or PE 4')], max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_name', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('time_slot', models.CharField(choices=[('11', 'Monday Course 1'), ('12', 'Monday Course 2'), ('13', 'Monday Course 3'), ('14', 'Monday Course 4'), ('21', 'Tuesday Course 1'), ('22', 'Tuesday Course 2'), ('23', 'Tuesday Course 3'), ('24', 'Tuesday Course 4'), ('31', 'Wednesday Course 1'), ('32', 'Wednesday Course 2'), ('33', 'Wednesday Course 3'), ('34', 'Wednesday Course 4'), ('41', 'Thursday Course 1'), ('42', 'Thursday Course 2'), ('43', 'Thursday Course 3'), ('44', 'Thursday Course 4'), ('51', 'Friday Course 1'), ('52', 'Friday Course 2'), ('53', 'Friday Course 3'), ('54', 'Friday Course 4')], max_length=5)),
                ('course_cat', models.CharField(choices=[('pe1or3', 'PE 1 or PE 3'), ('pe2or4', 'PE 2 or PE 4')], max_length=20)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=5)),
                ('max_numebr', models.IntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Selection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_slot', models.CharField(choices=[('11', 'Monday Course 1'), ('12', 'Monday Course 2'), ('13', 'Monday Course 3'), ('14', 'Monday Course 4'), ('21', 'Tuesday Course 1'), ('22', 'Tuesday Course 2'), ('23', 'Tuesday Course 3'), ('24', 'Tuesday Course 4'), ('31', 'Wednesday Course 1'), ('32', 'Wednesday Course 2'), ('33', 'Wednesday Course 3'), ('34', 'Wednesday Course 4'), ('41', 'Thursday Course 1'), ('42', 'Thursday Course 2'), ('43', 'Thursday Course 3'), ('44', 'Thursday Course 4'), ('51', 'Friday Course 1'), ('52', 'Friday Course 2'), ('53', 'Friday Course 3'), ('54', 'Friday Course 4')], max_length=5)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SpecialReq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='special_req',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='course.SpecialReq'),
        ),
    ]
