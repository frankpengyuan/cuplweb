from collections import defaultdict
from itertools import groupby

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from ratelimit.decorators import ratelimit

from ioadmin.models import SiteSetting
from .utils import system_online_required
from .models import DAYSLOT, Course, Student, Selection, SpecialReq, StudentReq


def error_handler(request):
	return redirect('index')


def offline(request):
	return HttpResponse("系统已下线。")


@system_online_required
@ratelimit(key='ip', rate='10/m', block=True)
def mylogin(request):
	context = {}
	if request.user.is_authenticated():
		if request.user.is_superuser == True:
			return redirect('/admin')
		return redirect('index')
	if request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '').lower()
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			request.session.set_expiry(0)
			if user.is_superuser == True:
				return redirect('/admin')
			return redirect('index')
		else:
			context['error'] = "学号或身份证号错误"
			return render(request, "login.html", context)

	return render(request, "login.html", context)


@system_online_required
def mylogout(request):
	logout(request)
	request.session.flush()
	request.session.modified = True
	return redirect('mylogin')


@system_online_required
@login_required
def index(request):
	settings = SiteSetting.objects.get()
	context = {
		"notification": settings.notification,
		"fail_msg": settings.fail_msg,
	}
	return render(request, "index.html", context)


@system_online_required
@login_required
def userinfo(request):
	if not request.session.get('course_cat', False):
		request.session["course_cat"] = request.user.course_cat
	initial_spec_in_session(request)
	initial_selected_in_session(request)
	context = _get_confirm_info(request)
	return render(request, "userinfo.html", context)


@system_online_required
@login_required
def choose_cat(request):
	context = {}
	if request.method == 'POST':
		if "selectable" in request.session:
			del request.session["selectable"]
		if request.POST["cat"] == "pe1or2":
			request.session["course_cat"] = "pe1or2"
		elif request.POST["cat"] == "pe3or4":
			request.session["course_cat"] = "pe3or4"
		else:
			return redirect('/')
		return redirect('/special_req/0')

	if not request.session.get('course_cat', False):
		request.session["course_cat"] = request.user.course_cat
	if request.session.get('course_cat') == "pe1or2":
		context["primary1"] = True
	elif request.session.get('course_cat') == "pe3or4":
		context["primary2"] = True

	context["spring_semester"] = SiteSetting.objects.get().course_cat == "1"
	return render(request, "choose_cat.html", context)


def initial_spec_in_session(request):
	if "all_req_flags" in request.session:
		return
	all_special_reqs = SpecialReq.objects.all().order_by("name")
	all_req_names, all_req_flags, all_req_context = [], [], []
	for req in all_special_reqs:
		flag = StudentReq.objects.filter(
			student_id=request.user.username,
			special_req_id=req.id,
		).count() > 0
		all_req_names.append(req.name)
		all_req_context.append(req.description)
		all_req_flags.append(flag)
	request.session["all_req_names"] = all_req_names
	request.session["all_req_context"] = all_req_context
	request.session["all_req_flags"] = all_req_flags


def handle_spec_update(request, special_req_idx):
	if request.POST["choose"] == "true":
		request.session["all_req_flags"][special_req_idx] = True
	elif request.POST["choose"] == "false":
		request.session["all_req_flags"][special_req_idx] = False


@system_online_required
@login_required
def special_req(request, special_req_idx):
	special_req_idx = int(special_req_idx)

	if request.method == 'POST':
		if "selectable" in request.session:
			del request.session["selectable"]
		handle_spec_update(request, special_req_idx)
		request.session.modified = True
		return redirect("/special_req/"+str(special_req_idx+1))

	context = {}
	initial_spec_in_session(request)
	special_reqs = list(zip(
		request.session.get("all_req_names"),
		request.session.get("all_req_context"),
		request.session.get("all_req_flags"),
	))
	if special_req_idx >= 0 and special_req_idx < len(special_reqs):
		context["begin"] = special_req_idx == 0
		context["end"] = special_req_idx == len(special_reqs) - 1
		context["special_req"] = special_reqs[special_req_idx]
		context["special_req_idx"] = special_req_idx
	else:
		return redirect("/timetable/1")
	return render(request, "special_req.html", context)


def initial_selectable_in_session(request):
	if "selectable" in request.session:
		return

	request.session["selectable"] = {day: list() for day in ["1", "2", "3", "4", "5"]}
	query = '''SELECT DISTINCT day_slot, time_slot FROM 
        (SELECT * FROM course_course LEFT JOIN course_specialreq ON true) AS t1
        WHERE course_cat='{}' AND
        (gender='{}' OR gender='B') AND
        (special_req_id IS NULL OR
        special_req_id IN
        (SELECT special_req_id FROM course_studentreq
        WHERE student_id='{}'))
        ORDER BY day_slot ASC;'''.format(
		request.session["course_cat"],
		request.user.gender,
		request.user.username,
	)
	
	with connection.cursor() as cursor:
		cursor.execute(query)
		selectable_raw = cursor.fetchall()
	for day_slot, day_data in groupby(selectable_raw, lambda x: x[0]):
		request.session["selectable"][day_slot] = sorted([d[1] for d in day_data])


def initial_selected_in_session(request):
	if "selected" in request.session:
		return

	selected_raw = Selection.objects.filter(
		student_id=request.user.username,
	).order_by("day_slot", "time_slot")

	request.session["selected"] = defaultdict(list)
	for day_slot, day_data in groupby(selected_raw, lambda x: x.day_slot):
		day_selections = list(day_data)
		request.session["selected"][day_slot] = [s.time_slot for s in day_selections]


def make_selected_valid(request):
	if "selectable" not in request.session:
		initial_selectable_in_session(request)
	if "selected" not in request.session:
		return

	for day in DAYSLOT:
		weekday = day[0]
		selected_of_day = [d for d in request.session["selected"][weekday]
			if d in request.session["selectable"][weekday]]
		request.session["selected"][weekday] = selected_of_day


def get_cur_selected_num(request):
	selected_num = 0
	for day in DAYSLOT:
		selected_num += len(request.session["selected"][day[0]])
	return selected_num


def get_selectable(request, weekday):
	# weekday: string (char) "1"-"5"
	selectable = [False] * 4
	for select in request.session["selectable"][weekday]:
		selectable[int(select)-1] = True
	return selectable


def get_selected(request, weekday):
	# weekday: string (char) "1"-"5"
	selected = [False] * 4
	for select in request.session["selected"][weekday]:
		selected[int(select)-1] = True
	return selected


def handle_selection_update(request, weekday, errors):
	new_selection = []
	for name in ["1", "2", "3", "4"]:
		if request.POST[name] == "True":
			new_selection.append(name)
	request.session["selected"][weekday] = new_selection
	make_selected_valid(request)
	request.session.modified = True
	if request.POST["to"] == "prev" and int(weekday) > 1:
		return redirect("/timetable/"+str(int(weekday)-1))
	elif request.POST["to"] == "next" and int(weekday) < 5:
		return redirect("/timetable/"+str(int(weekday)+1))
	elif request.POST["to"] == "next" and int(weekday) == 5:
		min_select_count = SiteSetting.objects.get().min_select_count
		if get_cur_selected_num(request) < min_select_count:
			errors.append("请至少选择{}节可上课时间".format(min_select_count))
		return redirect("confirm")


@system_online_required
@login_required
def timetable(request, weekday):
	errors = []
	if request.method == 'POST':
		redir = handle_selection_update(request, weekday, errors)
		if len(errors) == 0 and redir is not None:
			return redir

	time_slots = range(1, 5)
	slot_names = ["第一大节", "第二大节", "第三大节", "第四大节"]
	weekday_names = ["周一", "周二", "周三", "周四", "周五"]
	initial_selectable_in_session(request)
	initial_selected_in_session(request)
	make_selected_valid(request)
	request.session.modified = True

	selected = get_selected(request, weekday)
	selectable = get_selectable(request, weekday)
	
	context = {
		"cur_selected_num": get_cur_selected_num(request),
		"errors": errors,
		"min_select_count": SiteSetting.objects.get().min_select_count,
		"time_slots": zip(time_slots, slot_names, selected, selectable),
		"weekday": weekday,
		"weekday_name": weekday_names[int(weekday)-1],
	}
	return render(request, "timetable.html", context)


def save_data(request):
	request.user.course_cat = request.session["course_cat"]
	request.user.save()

	StudentReq.objects.filter(student_id=request.user.username).delete()
	special_reqs = []
	for idx, name in enumerate(request.session["all_req_names"]):
		if request.session["all_req_flags"][idx] == True:
			special_reqs.append(StudentReq(
				student_id=request.user.username,
				special_req=SpecialReq.objects.get(name=name),
			))
	StudentReq.objects.bulk_create(special_reqs)

	Selection.objects.filter(student_id=request.user.username).delete()
	selections = []
	for day in ["1", "2", "3", "4", "5"]:
		for select in request.session["selected"][day]:
			selections.append(Selection(
				student_id=request.user.username,
				day_slot=day,
				time_slot=select,
			))
	Selection.objects.bulk_create(selections)


def _get_confirm_info(request):
	context = {}
	semester = SiteSetting.objects.get().course_cat
	if request.session["course_cat"] == "pe1or2":
		if semester == "1":
			context["course_cat"] = "专项2"
		else:
			context["course_cat"] = "专项1"
	elif request.session["course_cat"] == "pe3or4":
		if semester == "1":
			context["course_cat"] = "专项4"
		else:
			context["course_cat"] = "专项3"
	else:
		context["course_cat"] = "未选择"
	
	slot_names = ["第一大节", "第二大节", "第三大节", "第四大节"]
	weekday_names = ["周一", "周二", "周三", "周四", "周五"]

	context["special_reqs"] = []
	for idx, name in enumerate(request.session["all_req_names"]):
		if request.session["all_req_flags"][idx] == True:
			choose_disp = "是"
		else:
			choose_disp = "否"
		context["special_reqs"].append({
			"name": name,
			"choose_disp": choose_disp,
		})

	context["selections"] = []
	for day in ["1", "2", "3", "4", "5"]:
		for select in request.session["selected"][day]:
			context["selections"].append({
				"day_slot": weekday_names[int(day)-1],
				"time_slot": slot_names[int(select)-1],
			})
	return context


@system_online_required
@login_required
def confirm(request):
	if request.method == 'POST':
		save_data(request)
		return redirect("finish")

	for key in ["course_cat", "selected", "all_req_names", "all_req_flags"]:
		if key not in request.session:
			return redirect("index")
	
	context = _get_confirm_info(request)
	return render(request, "confirm.html", context)


@system_online_required
def finish(request):
	logout(request)
	return render(request, "finish.html")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_delete(request):
	Course.objects.all().delete()
	Student.objects.filter(is_superuser=False).delete()
	Selection.objects.all().delete()
	SpecialReq.objects.all().delete()
	StudentReq.objects.all().delete()
	return redirect("/admin/ioadmin/iostudent/")


@system_online_required
def ratelimit_view(request, exception):
	return HttpResponse("尝试过于频繁，请过1分钟后重试！")
