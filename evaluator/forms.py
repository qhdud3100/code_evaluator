from allauth.account.forms import LoginForm
from django.forms import ModelForm

from evaluator.models import Submission, Classroom


class GoogleSocialLoginForm(LoginForm):

    def login(self, *args, **kwargs):
        return super().login(*args, **kwargs)


class ClassForm(ModelForm):

    class Meta:
        model = Classroom
        fields = [
            'name',
            'status'
        ]
class SubmissionForm(ModelForm):

    class Meta:
        model = Submission
        fields = [
            'description',
            'file'
        ]