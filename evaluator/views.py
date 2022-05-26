from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.urls import reverse_lazy

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
        context = super(ClassDetail,self).get_context_data()
        context['assignments'] = Assignment.objects.filter(
            classroom=self.object,

        ).order_by('-created')
        return context

class ClassCreate(LoginRequiredMixin, CreateView):
    template_name = 'evaluator/class_create.html'
    queryset = Classroom.objects.all()
    form_class = ClassForm
    success_url = reverse_lazy('evaluator:class_list')


class StudentList(LoginRequiredMixin, TemplateView):
    template_name = 'evaluator/student_list.html'

class EvaluationResult(LoginRequiredMixin, ListView):
    template_name = 'evaluator/evaluation_result.html'
    queryset = Submission.objects.all()

class AssignmentUpload(LoginRequiredMixin,CreateView):
    template_name = 'evaluator/assignment_upload.html'
    queryset = Classroom.objects.all()
    form_class = SubmissionForm
    success_url = reverse_lazy('evaluator:class_detail')

    def form_valid(self, form):
        temp_profile = form.save(commit=False)
        temp_profile.user = self.request.user
        temp_profile.save()

        return super().form_valid(form)
class AssignmentNotice(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/assignment_notification.html'
    queryset = Assignment.objects.all()
