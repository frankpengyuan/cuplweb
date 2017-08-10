from django import forms
from django.db import connection
from django.contrib import admin
from django.contrib.auth.models import Group
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe

from .models import SiteSetting, IOStudent
from course.models import Student, Course, SpecialReq


admin.site.unregister(Group)


class FieldException(Exception):
	pass


# # Register your models here.
class SiteSettingAdmin(admin.ModelAdmin):
	change_form_template = 'admin/site_setting_form.html'
	def change_view(self, request, object_id, form_url='', extra_context=None):
		# handle request
		return super(SiteSettingAdmin, self).change_view(request, object_id,
			form_url, extra_context=extra_context)

	def changelist_view(self, request, extra_context=None):
		return self.changeform_view(
			request, object_id='1', form_url='', extra_context=extra_context)
	
	def add_view(self, request, form_url='', extra_context=None):
		return self.changeform_view(
			request, object_id='1', form_url='', extra_context=extra_context)

	def delete_view(self, request, object_id, extra_context=None):
		return self.changeform_view(
			request, object_id='1', form_url='', extra_context=extra_context)
	

def handle_uploaded_file(f, dir_file):
    with open('uploads/'+dir_file, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def _get_gender(data, for_course=False):
	if data == '男':
		return 'M'
	elif data == '女':
		return 'F'
	else:
		if not for_course:
			raise FieldException("gender error") 
		else:
			return 'B'


def store_stu_info(fname, grade_lv):
	students = []
	failed = []
	mfile = open('uploads/'+fname, 'r')
	try:
		for line_n, line in enumerate(mfile):
			fields = [field.strip() for field in line.strip().split(',')]
			target_fields = ['XM', 'XB', 'XH', 'SFZH']
			if line_n == 0:
				if any(t not in fields for t in target_fields):
					return ("", mark_safe("导入失败，请确认文件包含以下列：<br>"+' '.join(target_fields)))
				header_dict = {
					'XM': fields.index("XM"),
					'XB': fields.index("XB"),
					'XH': fields.index("XH"),
					'SFZH': fields.index("SFZH"),
				}
			elif fields[header_dict['XH']] != '':
				gender = _get_gender(fields[header_dict['XB']])
				try:
					students.append(
						'('+', '.join([
						"\'"+fields[header_dict['XH']]+"\'",
						"\'"+fields[header_dict['SFZH']][-8:]+"\'",
						'\'0\'',
						'\'0\'',
						"\'"+gender+"\'",
						'\'\'',
						'\'1\'',
						])+')'
					)
				except FieldException as e:
					failed.append(line)
	except UnicodeError as e:
		failed.append(line)
	query = '''
		INSERT INTO course_student (username, password, is_staff, is_superuser, gender, course_cat, auto_match)
		VALUES %s
		ON DUPLICATE KEY UPDATE password=VALUES(password), gender=VALUES(gender);
	''' % ', '.join(students)

	with connection.cursor() as cursor:
		cursor.execute(query)

	mfile.close()
	if len(failed) == 0:
		return "导入完成！共导入"+str(len(students))+"人", ""
	else:
		return (mark_safe("导入完成！共导入"+str(len(students))+"人<br>"),
			mark_safe("以下信息导入失败，请手动录入：<br>"+'<br>'.join(failed)))


def _get_course_cat(data):
	if '一' in data or '二' in data:
		return 'pe1or2'
	elif '三' in data or '四' in data:
		return 'pe3or4'
	else:
		raise FieldException("pe1/2 or pe3/4 error")


def _get_course_time(fields, indices):
	mapping = {
		'1-2':'1',
		'3-4':'2',
		'6-7':'3',
		'8-9':'4',
	}
	for day in range(5):
		if fields[indices[day]] != '' and fields[indices[day]] in mapping:
			return str(day+1), mapping[fields[indices[day]]]
	raise FieldException("no time slot found for course\n"+','.join(fields))


def _get_special_req(data):
	if SpecialReq.objects.filter(name=data).count() == 0:
		return None
	else:
		return SpecialReq.objects.get(name=data)


def store_course_info(fname):
	mfile = open('uploads/'+fname, 'r')
	courses = []
	failed = []
	try:
		for line_n, line in enumerate(mfile):
			fields = [field.strip() for field in line.strip().split(',')]
			target_fields = ["课序", "课程名", "课容量", "选课人数", "星期一",
				"星期二", "星期三", "星期四", "星期五", "性别", "特别要求"]
			if line_n == 0:
				if any(t not in fields for t in target_fields):
					return ("", mark_safe("导入失败，请确认文件包含以下列：<br>"+' '.join(target_fields)))
				header_dict = {
					'course_idx': fields.index("课序"),
					'course_name': fields.index("课程名"),
					'capacity': fields.index("课容量"),
					'cur_num': fields.index("选课人数"),
					'week_days': [
						fields.index("星期一"),
						fields.index("星期二"),
						fields.index("星期三"),
						fields.index("星期四"),
						fields.index("星期五"),
					],
					'gender': fields.index("性别"),
					'special_req': fields.index("特别要求"),
				}
			elif fields[header_dict['course_name']] != '':
				course_name = '-'.join([
					fields[header_dict['course_name']],
					fields[header_dict['course_idx']],
				])
				special_req = fields[header_dict['special_req']]
				if (special_req != '' and SpecialReq.objects.filter(name=special_req).count() == 0):
					new_spe = SpecialReq.objects.create(name=special_req, description='')
					new_spe.save()
				try:
					courses.append(Course(
						course_name=course_name,
						day_slot=_get_course_time(fields, header_dict['week_days'])[0],
						time_slot=_get_course_time(fields, header_dict['week_days'])[1],
						course_cat=_get_course_cat(course_name),
						gender=_get_gender(fields[header_dict['gender']], for_course=True),
						special_req=_get_special_req(special_req),
						cur_number=fields[header_dict['cur_num']],
						max_number=fields[header_dict['capacity']],
						auto_match=True,
					))
				except FieldException as e:
					failed.append(line)
	except UnicodeError as e:
		failed.append(line)

	mfile.close()
	Course.objects.all().delete()
	Course.objects.bulk_create(courses)
	if len(failed) == 0:
		return "导入完成！共导入"+str(len(courses))+"项课程", ""
	else:
		return (mark_safe("导入完成！共导入"+str(len(courses))+"项课程<br>"),
			mark_safe("以下信息导入失败，请手动录入：<br>"+'<br>'.join(failed)))


class IOStudentAdmin(admin.ModelAdmin):
	change_list_template = 'admin/io_files.html'
	def change_view(self, request, object_id, form_url='', extra_context=None):
		return self.changelist_view(request, extra_context=extra_context)

	def changelist_view(self, request, extra_context=None):
		# handle request
		if request.method == 'POST':
			if "student_form" in request.POST and 'file' in request.FILES:
				handle_uploaded_file(request.FILES['file'], request.POST['grade']+'.csv')
				succ_msg, fail_msg = store_stu_info(request.POST['grade']+'.csv', request.POST['grade'])
				extra_context = extra_context or {}
				extra_context['succ_msg'] = succ_msg
				if fail_msg != '':
					extra_context['fail_msg'] = fail_msg
			elif "course_form" in request.POST:
				handle_uploaded_file(request.FILES['file'], 'courses.csv')
				succ_msg, fail_msg = store_course_info('courses.csv')
				extra_context = extra_context or {}
				extra_context['succ_msg'] = succ_msg
				if fail_msg != '':
					extra_context['fail_msg'] = fail_msg
			elif "action_form" in request.POST:
				pass
		return super(IOStudentAdmin, self).changelist_view(
			request, extra_context=extra_context)
	
	def add_view(self, request, form_url='', extra_context=None):
		return self.changelist_view(request, extra_context=extra_context)

	def delete_view(self, request, object_id, extra_context=None):
		return self.changelist_view(request, extra_context=extra_context)


admin.site.register(SiteSetting, SiteSettingAdmin)
admin.site.register(IOStudent, IOStudentAdmin)
