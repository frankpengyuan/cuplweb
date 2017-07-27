from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
	return render(request, "index.html")


def mylogin(request):
	context = {}
	if request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('index')
		else:
			context['error'] = "学号或身份证号错误"
			return render(request, "login.html", context)

	return render(request, "login.html", context)
