from collections import defaultdict
from itertools import groupby

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect

from ioadmin.models import SiteSetting
from .utils import system_online_required
from .models import DAYSLOT, Selection, SpecialReq, StudentReq


def error_handler(request):
	return redirect('index')


def offline(request):
	return HttpResponse("系统已下线。")


@system_online_required
def mylogin(request):
	context = {}
	if request.user.is_authenticated():
		return redirect('index')
	if request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			request.session.set_expiry(0)
			return redirect('index')
		else:
			context['error'] = "学号或身份证号错误"
			return render(request, "login.html", context)

	return render(request, "login.html", context)


@system_online_required
def mylogout(request):
	logout(request)
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
	selections = Selection.objects.filter(student=request.user.username)
	context = {"selections": selections}
	return render(request, "userinfo.html", context)


@system_online_required
@login_required
def choose_cat(request):
	context = {}
	if request.method == 'POST':
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

	request.session["selectable"] = defaultdict(list)
	query = '''SELECT DISTINCT course_course.day_slot, course_course.time_slot
        FROM course_course LEFT JOIN course_specialreq 
        ON course_course.course_cat='pe1or2' AND
        (course_course.gender='M' OR course_course.gender='') AND
        (course_course.special_req_id IS NULL OR
        course_course.special_req_id IN
        (SELECT course_studentreq.special_req_id FROM course_studentreq
        WHERE course_studentreq.student_id='2015101001'))
        ORDER BY course_course.day_slot ASC;'''.format(
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
		student=request.user.username,
	).order_by("day_slot", "time_slot")

	request.session["selected"] = defaultdict(list)
	for day_slot, day_data in groupby(selected_raw, lambda x: x.day_slot):
		request.session["selected"][day_slot] = sorted(list(day_data))


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
		if get_cur_selected_num(request) < 3:
			errors.append("请至少选择3节可上课时间")
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
	slot_names = ["一大", "二大", "三大", "四大"]
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
		"time_slots": zip(time_slots, slot_names, selected, selectable),
		"weekday": weekday,
		"weekday_name": weekday_names[int(weekday)-1],
	}
	return render(request, "timetable.html", context)


@system_online_required
@login_required
def confirm(request):
	return HttpResponse("confirm")