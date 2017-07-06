from django.db import models

# Create your models here.


class Course(models.Model):
    course_name = models.CharField(max_length=200, primary_key=True)


class Student(models.Model):
	student_id = models.CharField(max_length=40, primary_key=True)


class Selection(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    time_slot = models.CharField(max_length=5)
