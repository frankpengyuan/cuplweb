from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student, Course, SpecialReq


class CourseAdmin(admin.ModelAdmin):
	list_display = ["course_name", "time_slot", "course_cat", "gender", "special_req", "max_numebr"]


class SpecialReqAdmin(admin.ModelAdmin):
	list_display = ["name", "description"]


admin.site.register(Student, UserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(SpecialReq, SpecialReqAdmin)