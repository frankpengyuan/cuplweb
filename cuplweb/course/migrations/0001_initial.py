# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-04 05:33
from __future__ import unicode_literals

import course.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(error_messages={'unique': '用户已存在'}, max_length=30, primary_key=True, serialize=False, verbose_name='学号')),
                ('password', models.CharField(help_text='身份证号后8位，字母请大写', max_length=128, validators=[django.core.validators.RegexValidator('^([0-9]{7}[A-X]{1})|([0-9]{8})$', '身份证号后8位，字母请大写', 'invalid')], verbose_name='身份证号后8位')),
                ('is_staff', models.BooleanField(default=False, verbose_name='管理员')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='超级管理员')),
                ('gender', models.CharField(choices=[('M', '男'), ('F', '女')], max_length=5, verbose_name='性别')),
                ('course_cat', models.CharField(blank=True, choices=[('pe1or2', '体育1或2'), ('pe3or4', '体育3或4')], default='', max_length=20, verbose_name='上课类别')),
                ('auto_match', models.BooleanField(default=True, verbose_name='参与自动排课')),
            ],
            options={
                'verbose_name_plural': '学生',
                'verbose_name': '学生',
            },
            managers=[
                ('objects', course.models.StudentManager()),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_name', models.CharField(max_length=200, primary_key=True, serialize=False, verbose_name='课程名称')),
                ('day_slot', models.CharField(choices=[('1', '周一'), ('2', '周二'), ('3', '周三'), ('4', '周四'), ('5', '周五')], max_length=5, verbose_name='上课日期')),
                ('time_slot', models.CharField(choices=[('1', '一大'), ('2', '二大'), ('3', '三大'), ('4', '四大')], max_length=5, verbose_name='上课时间')),
                ('course_cat', models.CharField(choices=[('pe1or2', '体育1或2'), ('pe3or4', '体育3或4')], max_length=20, verbose_name='课程类别')),
                ('gender', models.CharField(choices=[('M', '男'), ('F', '女'), ('B', '均可')], max_length=5, verbose_name='性别要求')),
                ('cur_number', models.IntegerField(default=0, verbose_name='已注册人数')),
                ('max_number', models.IntegerField(default=100, verbose_name='最大容量')),
                ('auto_match', models.BooleanField(default=True, verbose_name='参与自动排课')),
            ],
            options={
                'verbose_name_plural': '课程',
                'verbose_name': '课程',
            },
        ),
        migrations.CreateModel(
            name='Selection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_slot', models.CharField(choices=[('1', '周一'), ('2', '周二'), ('3', '周三'), ('4', '周四'), ('5', '周五')], max_length=5, verbose_name='星期几')),
                ('time_slot', models.CharField(choices=[('1', '一大'), ('2', '二大'), ('3', '三大'), ('4', '四大')], max_length=5, verbose_name='时间')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='学生')),
            ],
            options={
                'verbose_name': '学生选择',
                'verbose_name_plural': '学生选择',
            },
        ),
        migrations.CreateModel(
            name='SpecialReq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='名称')),
                ('description', models.TextField(max_length=200, verbose_name='介绍')),
            ],
            options={
                'verbose_name_plural': '课程特殊要求',
                'verbose_name': '课程特殊要求',
            },
        ),
        migrations.CreateModel(
            name='StudentReq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('special_req', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.SpecialReq', verbose_name='特殊要求')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='学生')),
            ],
            options={
                'verbose_name': '学生特殊要求',
                'verbose_name_plural': '学生特殊要求',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='special_req',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='course.SpecialReq', verbose_name='特殊要求'),
        ),
        migrations.AddField(
            model_name='student',
            name='course',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.Course', verbose_name='排课'),
        ),
        migrations.AddField(
            model_name='student',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='student',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='studentreq',
            unique_together=set([('student', 'special_req')]),
        ),
        migrations.AlterUniqueTogether(
            name='selection',
            unique_together=set([('student', 'day_slot', 'time_slot')]),
        ),
    ]
