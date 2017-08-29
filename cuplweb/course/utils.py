from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from ioadmin.models import SiteSetting


def system_online_required(func):
    def func_wrapper(*args, **kwargs):
        settings = SiteSetting.objects.get()
        if settings.online_flag:
            return func(*args, **kwargs)
        else:
            return redirect('offline')
    return func_wrapper


class IDValidator(object):
    """
    custom validator for password/身份证号后8位
    """
    def __init__(self, length=8):
        self.length = length

    def validate(self, password, user=None):
        if len(password) != self.length:
            raise ValidationError(
                "请输入身份证号后8位",
                code='password_err',
                params={'length': self.length},
            )

    def get_help_text(self):
        return "请输入身份证号后8位"
