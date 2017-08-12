import csv
from django.http import HttpResponse

from course.models import (
	Course,
	Selection,
	SpecialReq,
	Student,
	StudentReq,
)


def schedule_courses():
	succ_msg = ""
	fail_msg = ""
	return succ_msg, fail_msg


def _check_in_selections(day, time, selections):
	for selection in selections:
		if selection.day_slot == day and selection.time_slot == time:
			return True
	return False


def _check_in_req(special_req, stu_special_reqs):
	for stu_req in stu_special_reqs:
		if stu_req.special_req_id == special_req.id:
			return True
	return False


def generate_results():
	with open('uploads/results.csv', encoding='utf-8', mode='w+') as mfile:
		header = ("学号,性别,专项,"
			"1_1,1_2,1_3,1_4,2_1,2_2,2_3,2_4,3_1,3_2,3_3,3_4,4_1,4_2,4_3,4_4,5_1,5_2,5_3,5_4,"
			"{},"
			"排课结果").format(",".join(spe.name for spe in SpecialReq.objects.all().order_by("id")))
		mfile.write(header + '\n')

		student_ids_p1 = set(Selection.objects.values_list("student_id", flat=True).distinct())
		student_ids_p2 = set(Student.objects.filter(
			course_id__isnull=False).values_list("username", flat=True).distinct())
		student_ids = student_ids_p1 | student_ids_p2
		for student_id in student_ids:
			student = Student.objects.get(username=student_id)
			line_buffer = []
			line_buffer.append(student.username)
			line_buffer.append(student.get_gender_display())
			line_buffer.append(student.get_course_cat_display())
			selections = Selection.objects.filter(student_id=student.username)
			for day in ["1", "2", "3", "4", "5"]:
				for time in ["1", "2", "3", "4"]:
					if _check_in_selections(day, time, selections):
						line_buffer.append("1")
					else:
						line_buffer.append("")
			stu_special_reqs = StudentReq.objects.filter(student_id=student.username)
			for special_req in SpecialReq.objects.all().order_by("id"):
				if _check_in_req(special_req, stu_special_reqs):
					line_buffer.append("1")
				else:
					line_buffer.append("")
			line_buffer.append(student.course_id or "")
			mfile.write(",".join(line_buffer) + '\n')

	with open('uploads/results.csv', encoding='utf-8', mode='r') as mfile:
		data = mfile.read()
	response = HttpResponse(data, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="results.csv"'
	response['X-Sendfile'] = "uploads/results.csv"
	return response
