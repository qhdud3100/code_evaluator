from allauth.account.forms import LoginForm
from django.forms import ModelForm

from evaluator import models
from evaluator.models import Assignment, Submission


class GoogleSocialLoginForm(LoginForm):

    def login(self, *args, **kwargs):
        return super().login(*args, **kwargs)


class SubmissionUploadForm(ModelForm):

    class Meta:
        model = Submission
        fields = '__all__'
