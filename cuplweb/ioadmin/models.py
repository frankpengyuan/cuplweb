from django.db import models


CAT = (("1", "春季"), ("2", "秋季"))


class SiteSetting(models.Model):
	course_cat = models.CharField(
		"学期",
		max_length=10,
		choices=CAT,
		default="1",
	)
	min_select_count = models.IntegerField('至少选择可上课节数', default=3)
	online_flag = models.BooleanField('系统上线', default=True)
	notification = models.TextField("登录提醒", blank=True, default='', max_length=300)
	fail_msg = models.TextField("到办公室登记说明", blank=True, default='', max_length=200)

	def __str__(self):
		return '网站设置'

	class Meta:
		verbose_name = '网站设置'
		verbose_name_plural = '网站设置'


class IOStudent(models.Model):

	def __str__(self):
		return '导入导出与自动排课'

	class Meta:
		verbose_name = '导入导出与自动排课'
		verbose_name_plural = '导入导出与自动排课'

