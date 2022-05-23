from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, CreateView

from evaluator.forms import ClassForm
from evaluator.models import Classroom


class ClassList(LoginRequiredMixin, ListView):
    template_name = 'evaluator/class_list.html'
    queryset = Classroom.objects.all()


class ClassDetail(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/class_detail.html'
    queryset = Classroom.objects.all()


class ClassCreate(LoginRequiredMixin, CreateView):
    template_name = 'evaluator/class_create.html'
    queryset = Classroom.objects.all()
    form_class = ClassForm


class StudentList(LoginRequiredMixin, TemplateView):
    template_name = 'evaluator/student_list.html'


class EvaluationResult(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/evaluation_result.html'
    object = None
