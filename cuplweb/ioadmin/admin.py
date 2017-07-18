from django import forms
from django.db import connection
from django.contrib import admin
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe

from .models import SiteSetting, IOStudent
from course.models import Student

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


def store_stu_info(fname, grade_lv):
	students = []
	failed = []
	mfile = open('uploads/'+fname, 'r')
	try:
		for line_n, line in enumerate(mfile):
			print('processing line ', line_n)
			print(line)
			fields = [field.strip() for field in line.strip().split(',')]
			if line_n == 0:
				header_dict = {
					'XM': fields.index("XM"),
					'XB': fields.index("XB"),
					'XH': fields.index("XH"),
					'SFZH': fields.index("SFZH"),
				}
			elif fields[header_dict['XH']] != '':
				if fields[header_dict['XB']] == '男':
					gender = 'M'
				elif fields[header_dict['XB']] == '女':
					gender = 'F'
				else:
					raise Exception("gender error")
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
				pass
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
