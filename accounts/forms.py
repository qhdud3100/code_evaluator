from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForm(forms.ModelForm):
    identifier_id = forms.IntegerField(label='Student/Staff ID', max_value=99999999)

    class Meta:
        model = User
        fields = ['identifier_id']
