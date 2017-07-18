from django.core.exceptions import ValidationError

class IDValidator(object):
    """
    custom validator for password/身份证号后8位
    """
    def __init__(self, length=8):
        self.length = length

    def validate(self, password, user=None):
        if len(password) != self.length:
            raise ValidationError(
                "请输入身份证号后8位，字母请大写",
                code='password_err',
                params={'length': self.length},
            )

    def get_help_text(self):
        return "请输入身份证号后8位，字母请大写"
