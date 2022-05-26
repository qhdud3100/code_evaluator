from pprint import pprint
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.urls import reverse_lazy, reverse

from evaluator.forms import ClassForm, SubmissionForm
from evaluator.models import Classroom, Assignment, Submission




class ClassList(LoginRequiredMixin, ListView):
    template_name = 'evaluator/class_list.html'
    queryset = Classroom.objects.all()
    paginate_by = 10


class ClassDetail(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/class_detail.html'
    queryset = Classroom.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ClassDetail, self).get_context_data()

        context['assignments'] = Assignment.objects.filter(
            classroom=self.object,
        ).order_by('-created')

        context['submissions'] = Submission.objects.filter(
            user=self.request.user,
        )

        return context



class ClassCreate(LoginRequiredMixin, CreateView):
    template_name = 'evaluator/class_create.html'
    queryset = Classroom.objects.all()
    form_class = ClassForm
    success_url = reverse_lazy('evaluator:class_list')


class StudentList(LoginRequiredMixin, TemplateView):
    template_name = 'evaluator/student_list.html'


class SubmissionCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'evaluator/submission_create.html'
    form_class = SubmissionForm
    success_url = reverse_lazy('evaluator:class_detail')
    success_message = 'Submission successfully uploaded.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['assignment'] = self.get_assignment()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('evaluator:assignment_notice', kwargs={'pk': self.kwargs['assignment_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = self.get_assignment()
        return context

    def get_assignment(self):
        return Assignment.objects.get(id=self.kwargs['assignment_pk'])


class AssignmentNotice(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/assignment_notification.html'
    queryset = Assignment.objects.all()

class EvaluationResult(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/evaluation_result.html'
    queryset = Submission.objects.all()


class FileDownloadView(SingleObjectMixin, View):
    queryset = Assignment.objects.all()

    def get(self, request, document_id):
        object = Assignment.objects.get(pk=document_id)
        file_path = object.attachment.path
        fs = FileSystemStorage(file_path)
        response = FileResponse(fs.open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename={object.attachment.name}'

        return response
