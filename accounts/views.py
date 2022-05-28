from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.forms import UserForm

User = get_user_model()


class UserUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'account/user_update.html'
    form_class = UserForm
    success_url = reverse_lazy('evaluator:class_list')
    success_message = 'Edit Successful.'

    def get_object(self, queryset=None):
        return self.request.user
