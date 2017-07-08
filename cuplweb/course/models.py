from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.

GENDER = (("M", "Male"), ("F", "Female"))
CAT = (("pe1or3", "PE 1 or PE 3"), ("pe2or4", "PE 2 or PE 4"))
TIMESLOT = [
	("11", "Monday Course 1"),
	("12", "Monday Course 2"),
	("13", "Monday Course 3"),
	("14", "Monday Course 4"),
	("21", "Tuesday Course 1"),
	("22", "Tuesday Course 2"),
	("23", "Tuesday Course 3"),
	("24", "Tuesday Course 4"),
	("31", "Wednesday Course 1"),
	("32", "Wednesday Course 2"),
	("33", "Wednesday Course 3"),
	("34", "Wednesday Course 4"),
	("41", "Thursday Course 1"),
	("42", "Thursday Course 2"),
	("43", "Thursday Course 3"),
	("44", "Thursday Course 4"),
	("51", "Friday Course 1"),
	("52", "Friday Course 2"),
	("53", "Friday Course 3"),
	("54", "Friday Course 4"),
]


class SpecialReq(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)


class Course(models.Model):
	course_name = models.CharField(max_length=200, primary_key=True)
	time_slot = models.CharField(max_length=5, choices=TIMESLOT)
	course_cat = models.CharField(max_length=20, choices=CAT)
	gender = models.CharField(max_length=5, choices=GENDER)
	special_req = models.ForeignKey(
		SpecialReq, default=None, null=True, on_delete=models.SET_NULL)
	max_numebr = models.IntegerField(default=100)

	cur_number = 0


class Student(AbstractUser):
	#username
	#password
	gender = models.CharField(max_length=5, choices=GENDER)
	course_cat = models.CharField(max_length=20, choices=CAT)


class Selection(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	time_slot = models.CharField(max_length=5, choices=TIMESLOT)


class ScheduleResult(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)

