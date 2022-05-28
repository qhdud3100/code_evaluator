from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class HandongSocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        email_domain = sociallogin.account.extra_data.get('hd')
        return email_domain in ['handong.ac.kr', 'handong.edu']

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)

        name_to_groups = {
            '학부생': Group.objects.filter(name='Student'),
            '교수님': Group.objects.filter(name='Instructor')
        }

        group = name_to_groups.get(user.last_name, Group.objects.filter(name='Student'))

        user.groups.set(group)
        return user
