from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.urls import reverse_lazy

from evaluator.forms import ClassForm
from evaluator.models import Classroom, Assignment


class ClassList(LoginRequiredMixin, ListView):
    template_name = 'evaluator/class_list.html'
    queryset = Classroom.objects.all()
    paginate_by = 10


class ClassDetail(LoginRequiredMixin, ListView):
    template_name = 'evaluator/class_detail.html'
    queryset = []

    def get_context_data(self, **kwargs):
        context = super(ClassDetail,self).get_context_data()
        context['Assignments'] = Assignment.objects.all().filter(pk=1)

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
    #object = None
    queryset = []
