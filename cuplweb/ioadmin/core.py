import csv
from collections import defaultdict

from django.http import HttpResponse

from course.models import (
	Course,
	Selection,
	SpecialReq,
	Student,
	StudentReq,
)


def _get_target_students():
	student_ids_p1 = set(Selection.objects.values_list("student_id", flat=True).distinct())
	student_ids_p2 = set(Student.objects.filter(
		course_id__isnull=False).values_list("username", flat=True).distinct())
	student_ids = student_ids_p1 | student_ids_p2
	students = Student.objects.filter(username__in=student_ids)
	for student in students:
		if student.auto_match == True:
			student.course = None
	return students


def _get_time_course_map(courses_list=None):
	if courses_list is None:
		courses_list = Course.objects.all()
	time_course_dict = defaultdict(lambda: defaultdict(list))
	for course in courses_list:
		time_course_dict[course.day_slot][course.time_slot].append(course)
	return time_course_dict


def _get_name_course_map(courses_list=None):
	if courses_list is None:
		courses_list = Course.objects.all()
	name_course_dict = {}
	for course in courses_list:
		name_course_dict[course.course_name] = course
	return name_course_dict


def _refresh_add_num(students=None, courses_list=None):
	if students is None:
		students = _get_target_students()
	if courses_list is None:
		courses_list = Course.objects.all()
	for course in courses_list:
		course.add_number = 0
	courses_dict = _get_name_course_map(courses_list)
	for student in students:
		if student.course_id is not None:
			courses_dict[student.course_id].add_number += 1


def _assign_student(student, course):
	student.course = course
	course.add_number += 1


def _reassign_student(student, old_course, new_course):
	old_course.add_number -= 1
	student.course = new_course
	new_course.add_number += 1


def _req_met(course, reqs):
	if course.special_req is None:
		return True
	for req in reqs:
		if req.special_req_id == course.special_req_id:
			return True
	return False


def _get_valid_courses(student, courses):
	valid_courses = []
	reqs = StudentReq.objects.filter(student_id=student.username)
	for course in courses:
		if course.auto_match == False:
			continue
		elif course.cur_number + course.add_number >= course.max_number:
			continue
		if course.gender == "B" or course.gender == student.gender:
			if _req_met(course, reqs):
				valid_courses.append(course)
	return valid_courses


def _get_min_number_course(courses):
	if len(courses) == 0:
		return None
	min_course = courses[0]
	for course in courses:
		if course.cur_number + course.add_number < min_course.cur_number + min_course.add_number:
			min_course = course
	return min_course


def _get_best_course(student, time_course_dict):
	selections = Selection.objects.filter(student_id=student.username)
	local_min_courses = []
	for selection in selections:
		local_min_course = _get_min_number_course(
			time_course_dict[selection.day_slot][selection.time_slot])
		if local_min_course is not None:
			local_min_courses.append(local_min_course)
	best_course = _get_min_number_course(local_min_courses)
	return best_course


def _save_to_db(students, courses):
	for student in students:
		student.save()
	for course in courses:
		course.save()


def _initial_assign(students, all_courses):
	for student in students:
		if student.auto_match == False or student.course is not None:
			continue
		valid_courses = _get_valid_courses(student, all_courses)
		if len(valid_courses) == 0:
			continue
		time_course_dict = _get_time_course_map(valid_courses)
		the_course = _get_best_course(student, time_course_dict)
		_assign_student(student, the_course)


def _reassign(students, all_courses):
	name_course_dict = _get_name_course_map(all_courses)
	for student in students:
		if student.auto_match == False:
			continue
		valid_courses = _get_valid_courses(student, all_courses)
		if len(valid_courses) == 0:
			continue
		time_course_dict = _get_time_course_map(valid_courses)
		the_course = _get_best_course(student, time_course_dict)
		if student.course is not None:
			old_course = name_course_dict[student.course_id]
			if the_course.cur_number+the_course.add_number < old_course.cur_number+old_course.add_number:
				_reassign_student(student, old_course, the_course)
		else:
			_assign_student(student, the_course)


def schedule_courses():
	students = _get_target_students()
	all_courses = Course.objects.all()

	_refresh_add_num(students, all_courses)
	_initial_assign(students, all_courses)
	for _ in range(5):
		_reassign(students, all_courses)
	_save_to_db(students, all_courses)

	succ_msg = "排课完成！"
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

		students = _get_target_students()
		for student in students:
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
