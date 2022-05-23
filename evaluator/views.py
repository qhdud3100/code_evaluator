from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, DetailView, TemplateView

from evaluator.forms import SubmissionUploadForm
from evaluator.models import Classroom


class ClassList(LoginRequiredMixin, ListView):
    template_name = 'evaluator/class_list.html'
    queryset = Classroom.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pprint(context)
        return context


class ClassDetail(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/class_detail.html'
    queryset = Classroom.objects.all()


class StudentList(LoginRequiredMixin, TemplateView):
    template_name = 'evaluator/student_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = [
            {
                'name': 'Juho Hong',
                'id': '21300833',
                'scores': [20, 1, 0, 90]
            },
            {
                'name': 'Chanhyo Lee',
                'id': '21700589',
                'scores': [19, 0, 1, 95]
            },
            {
                'name': 'BoYoung Yun',
                'id': '21800486',
                'scores': [17, 0, 3, 91]
            },
            {
                'name': 'Hyogyung Seo',
                'id': '21900371',
                'scores': [20, 0, 0, 98]
            },
            {
                'name': 'Seulgi Jeong',
                'id': '21900667',
                'scores': [20, 0, 0, 95]
            }
        ]

        context[''] = students
        return context


class SubmissionUpload(FormView):
    template_name = 'evaluator/assignment_upload.html'
    form_class = SubmissionUploadForm


class EvaluationResult(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/evaluation_result.html'
    object = None

