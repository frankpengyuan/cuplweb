from django.core import validators
from django.db import models
from django.contrib.auth.hashers import (
    check_password,
    make_password,
)
from django.contrib.auth.models import (
	AbstractBaseUser,
	BaseUserManager,
	PermissionsMixin,
)

# Create your models here.

CLS_GENDER = (("M", "男"), ("F", "女"), ("B", "均可"))
STU_GENDER = (("M", "男"), ("F", "女"),)
CAT = (("pe1or3", "体育1或3"), ("pe2or4", "体育2或4"))
TIMESLOT = [
	("11", "周一 一大"),
	("12", "周一 二大"),
	("13", "周一 三大"),
	("14", "周一 四大"),
	("21", "周二 一大"),
	("22", "周二 二大"),
	("23", "周二 三大"),
	("24", "周二 四大"),
	("31", "周三 一大"),
	("32", "周三 二大"),
	("33", "周三 一大"),
	("34", "周三 四大"),
	("41", "周四 一大"),
	("42", "周四 二大"),
	("43", "周四 三大"),
	("44", "周四 四大"),
	("51", "周五 一大"),
	("52", "周五 二大"),
	("53", "周五 三大"),
	("54", "周五 四大"),
]


class SpecialReq(models.Model):
	name = models.CharField("名称", max_length=50)
	description = models.CharField("介绍", max_length=200)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = '课程特殊要求'
		verbose_name_plural = '课程特殊要求'


class Course(models.Model):
	course_name = models.CharField("课程名称", max_length=200, primary_key=True)
	time_slot = models.CharField("上课时间", max_length=5, choices=TIMESLOT)
	course_cat = models.CharField("课程类别", max_length=20, choices=CAT)
	gender = models.CharField("性别要求", max_length=5, choices=CLS_GENDER)
	special_req = models.ForeignKey(
		SpecialReq, 
		default=None, 
		blank=True,
		null=True,
		on_delete=models.SET_NULL,
		verbose_name="特殊要求",
	)
	cur_number = models.IntegerField("已注册人数", default=0)
	max_number = models.IntegerField("最大容量", default=100)
	auto_match = models.BooleanField("参与自动排课", default=True)

	def __str__(self):
		return self.course_name

	class Meta:
		verbose_name = '课程'
		verbose_name_plural = '课程'


class StudentManager(BaseUserManager):
	use_in_migrations = True

	def _create_user(self, username, password,
					 is_staff, is_superuser, **extra_fields):
		if not username:
			raise ValueError('The given username must be set')
		user = self.model(username=username,
						  is_staff=is_staff,
						  is_superuser=is_superuser,
						  **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, password=None, **extra_fields):
		return self._create_user(username, password, False, False,
								 **extra_fields)

	def create_superuser(self, username, password, **extra_fields):
		return self._create_user(username, password, True, True,
								 **extra_fields)
		

class Student(AbstractBaseUser, PermissionsMixin):
	USERNAME_FIELD = "username"
	username = models.CharField(
		'学号', max_length=30, primary_key=True,
		error_messages={
			'unique': "用户已存在",
		}
	)
	password = models.CharField(
		'身份证号后8位',
		max_length=128,
		help_text='身份证号后8位，字母请大写',
		validators=[
			validators.RegexValidator(
				r'^([0-9]{7}[A-X]{1})|([0-9]{8})$',
				'身份证号后8位，字母请大写',
				'invalid',
			),
		],
	)
	is_staff = models.BooleanField('管理员', default=False)
	is_superuser = models.BooleanField('超级管理员', default=False)
	gender = models.CharField("性别", max_length=5, choices=STU_GENDER)
	course_cat = models.CharField(
		"上课类别",
		max_length=20,
		choices=CAT,
		blank=True,
		default='',
	)
	auto_match = models.BooleanField("参与自动排课", default=True)
	course = models.ForeignKey(
		Course,
		default=None, 
		blank=True,
		null=True,
		on_delete=models.CASCADE,
		verbose_name="排课",
	)

	objects = StudentManager()

	def __str__(self):
		return self.username

	class Meta:
		verbose_name = '学生'
		verbose_name_plural = '学生'

	def get_full_name(self):
		return self.username

	def get_short_name(self):
		return self.username

	def set_password(self, raw_password):
		if self.is_staff:
			self.password = make_password(raw_password)
		else:
			self.password = raw_password

	def check_password(self, raw_password):
		def setter(raw_password):
			self.set_password(raw_password)
			self.save(update_fields=["password"])
		if self.is_staff:
			return check_password(raw_password, self.password, setter)
		else:
			return self.password == raw_password

class Selection(models.Model):
	student = models.ForeignKey(
		Student, on_delete=models.CASCADE, verbose_name="学生")
	time_slot = models.CharField("时间", max_length=5, choices=TIMESLOT)

	class Meta:
		verbose_name = '学生选择'
		verbose_name_plural = '学生选择'
