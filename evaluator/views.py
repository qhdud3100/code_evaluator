import json
from pprint import pprint

from django.contrib import messages
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, FormView
from django.urls import reverse_lazy, reverse

from evaluator.forms import ClassForm, SubmissionForm, EditForm, AssignmentForm, ClassJoinForm
from evaluator.management.commands.evaluator import evaluate_submission
from evaluator.models import Classroom, Assignment, Submission


class ClassList(LoginRequiredMixin, ListView):
    template_name = 'evaluator/class_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Classroom.objects.visible(self.request.user)


class ClassDetail(LoginRequiredMixin, DetailView):
    template_name = 'evaluator/class_detail.html'

    def get_queryset(self):
        return Classroom.objects.visible(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['invitation_message'] = self.get_invitation_message()

        return context

    def get_invitation_message(self):
        return self.object.invitation_code


class ClassCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'evaluator/class_create.html'
    model = Classroom
    form_class = ClassForm
    success_url = reverse_lazy('evaluator:class_list')
    permission_required = 'classroom.create_classroom'

    def form_valid(self, form):
        form_valid = super().form_valid(form)

        if self.object.instructors != self.request.user:
            self.object.instructors.add(self.request.user)

        return form_valid


class ClassJoin(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'evaluator/class_join.html'
    form_class = ClassJoinForm
    success_url = reverse_lazy('evaluator:class_list')
    success_message = 'Class successfully joined.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class AssignmentCreate(LoginRequiredMixin, SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    template_name = 'evaluator/assignment_create.html'
    form_class = AssignmentForm
    success_url = reverse_lazy('evaluator:class_list')
    success_message = 'Submission successfully uploaded.'
    permission_required = 'assignment.create_assignment'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        return kwargs

    def get_success_url(self):
        return reverse_lazy('evaluator:class_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classroom'] = self.get_classroom()
        return context

    def get_classroom(self):
        return Classroom.objects.get(pk=self.kwargs['pk'])


class StudentList(LoginRequiredMixin, TemplateView):
    template_name = 'evaluator/student_list.html'


# class SubmissionUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
#     template_name = 'evaluator/submission_create.html'
#     form_class = SubmissionForm
#     model = Submission
#     success_url = reverse_lazy('evaluator:class_detail')
#     success_message = 'Submission successfully updated.'
#
#     def get_queryset(self):
#         if self.object.assignment.classroom.instructors == self.request.user:
#             return Submission.objects.filter(id=self.object.id)
#         else:
#             return Submission.objects.open(
#                 user=self.request.user
#             )
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['assignment'] = self.get_assignment()
#         kwargs['user'] = self.request.user
#         return kwargs
#
#     def get_success_url(self):
#         return reverse_lazy('evaluator:assignment_notice', kwargs={'pk': self.kwargs['assignment_pk']})
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['assignment'] = self.get_assignment()
#         return context
#
#     def get_assignment(self):
#         return Assignment.objects.get(id=self.kwargs['assignment_pk'])


class SubmissionCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'evaluator/submission_create.html'
    form_class = SubmissionForm
    success_url = reverse_lazy('evaluator:class_detail')
    success_message = 'Submission successfully uploaded.'

    def dispatch(self, request, *args, **kwargs):
        submission_exists = Submission.objects.filter(
            user=self.request.user,
            assignment=self.get_assignment()
        ).exists()
        if submission_exists:
            messages.warning(request, 'Not Allowed.')
            return redirect('evaluator:assignment_notice', pk=self.kwargs['assignment_pk'])

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        super().form_valid(form=form)

        assignment_path = self.object.assignment.answer_code.path
        input_file_path = self.object.file.path
        config_file_path = self.object.assignment.criteria.config_file.path
        test_case_path = self.object.assignment.test_case.path
        result = evaluate_submission(
            config_file_path,
            assignment_path,
            input_file_path,
            test_case_path
        )
        self.object.result = result
        self.object.save()

        return super().form_valid(form=form)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.object.result
        key_excluded = [
            'config_path',
            'compile_code',
            'execute_code',
            'compare_code',
            'lines'
        ]
        count_passed = 0
        count_failed = 0
        result_dictionary = {}
        for key, value in result.items():
            if key in key_excluded:
                continue

            for k, v in value.items():
                result_dictionary[k] = 'Pass' if v else 'Fail'
                if v:
                    count_passed += 1
                else:
                    count_failed += 1

        total_count = count_passed + count_failed

        context['total_count'] = total_count
        context['count_passed'] = count_passed
        context['count_failed'] = count_failed
        context['result_dictionary'] = result_dictionary
        return context


class AssignmentStatistics(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    template_name = 'evaluator/assignment_statistics.html'
    queryset = Assignment.objects.all()
    permission_required = 'assignment.edit_assignment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submissions'] = Submission.objects.filter(
            assignment=self.object
        ).first()
        return context


class FileDownloadView(SingleObjectMixin, View):
    queryset = Assignment.objects.all()

    def get(self, request, document_id):
        object = Assignment.objects.get(pk=document_id)
        file_path = object.attachment.path
        fs = FileSystemStorage(file_path)
        response = FileResponse(fs.open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename={object.attachment.name}'

        return response


class AssignmentEdit(LoginRequiredMixin, SuccessMessageMixin, PermissionRequiredMixin, UpdateView):
    model = Assignment.objects.all()
    template_name = 'evaluator/assignment_edit.html'
    form_class = EditForm
    success_url = reverse_lazy('evaluator:class_detail')
    success_message = 'Submission successfully uploaded.'
    context_object_name = 'edit'
    permission_required = 'assignment.edit_assignment'

    def get_success_url(self):
        return reverse_lazy('evaluator:assignment_notice', kwargs={'pk': self.kwargs['pk']})

    def get_object(self, queryset=None):
        edit = Assignment.objects.get(pk=self.kwargs['pk'])

        return edit
