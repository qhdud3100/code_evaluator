from pprint import pprint

from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from evaluator.models import Submission, Classroom, Assignment


User = get_user_model()

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
    # assignment = forms.ModelChoiceField(queryset=Assignment.objects.none())
    # user = forms.ModelChoiceField(queryset=User.objects.none())

    class Meta:
        model = Submission
        fields = [
            'description',
            'file',
            'assignment',
            'user'
        ]

    def __init__(self, *args, **kwargs):
        _assignment = kwargs.pop('assignment')
        _user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['assignment'].initial = _assignment
        self.fields['assignment'].widget = forms.HiddenInput()
        self.fields['user'].initial = _user
        self.fields['user'].widget = forms.HiddenInput()


    # def clean(self):
    #     cleaned_data = super().clean()
    #     cleaned_data['assignment_id'] = self._assignment.id
    #     cleaned_data['user'] = self._user
    #     return cleaned_data
