from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import Student, Course, SpecialReq

from course.models import CLS_GENDER, STU_GENDER, CAT


class CourseAdmin(admin.ModelAdmin):
	list_display = [
		"course_name", "time_slot", "course_cat", "gender",
		"special_req", "cur_number", "max_number", "auto_match",
	]
	fieldsets = [
		(None,		{'fields': ['course_name']}),
		('课程信息', {'fields': ['time_slot', 'course_cat', 'gender', 'special_req']}),
		('自动排课', {'fields': ['auto_match', 'cur_number', 'max_number']}),
	]
	search_fields = ['course_name']
	list_filter = ['course_cat', 'gender', 'time_slot']


class SpecialReqAdmin(admin.ModelAdmin):
	list_display = ['name', 'description']


class StudentForm(UserChangeForm):
	username = forms.CharField(label="学号")
	password = forms.CharField(label="身份证号后8位")
	gender = forms.ChoiceField(label="性别", choices=STU_GENDER)
	course_cat = forms.ChoiceField(label="上课类别", choices=CAT)

	class Meta:
		model = Student
		fields = ('__all__')

	def clean_password(self):
		password = self.cleaned_data.get("password")
		return password


class StudentFormFixed(StudentForm):
	username = forms.CharField(label="学号", disabled=True)
	password = forms.CharField(label="身份证号后8位", disabled=True)
	gender = forms.ChoiceField(label="性别", choices=STU_GENDER, required=False, disabled=True)
	course_cat = forms.ChoiceField(label="上课类别", choices=CAT, required=False, disabled=True)


class StudentAdmin(UserAdmin):
	# add_form_template = 'admin/auth/user/add_form.html'
	# change_list_template = 'admin/m_change_form.html'

	# def m_changelist_view(self, request, extra_context=None):
	# 	print(request)
	# 	return self.changelist_view(request, extra_context=extra_context)
	# changelist_view = m_changelist_view

	add_form_template = None
	fieldsets = []
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': (
				'username', 'password', 'gender',
				'course_cat', 'auto_match', 'course'
			),
		}),
	)
	
	form = StudentFormFixed
	add_form = StudentForm
	change_password_form = None
	list_display = ("username", 'gender',
				'course_cat', 'auto_match', 'course')
	list_filter = ('gender',
				'course_cat', 'auto_match', 'course')
	search_fields = ("username",)
	filter_horizontal = ()
	fields = (
		'username', 'password', 'gender',
		'course_cat', 'auto_match', 'course'
	)

	def get_form(self, request, obj=None, **kwargs):
		defaults = {}
		if obj is None:
			defaults['form'] = self.add_form
		defaults.update(kwargs)
		return super().get_form(request, obj, **defaults)


admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(SpecialReq, SpecialReqAdmin)