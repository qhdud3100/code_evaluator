from django.contrib import admin

# Register your models here.
from evaluator.models import Classroom, Assignment, Submission, Semester, Criterion


@admin.register(Classroom)
class Classroom(admin.ModelAdmin):
    list_display = ['pk', 'name']


@admin.register(Assignment)
class Assignment(admin.ModelAdmin):
    list_display = ['pk', 'name']


@admin.register(Submission)
class Submission(admin.ModelAdmin):
    list_display = ['pk', 'assignment']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_current']
    list_editable = ['is_current']


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = ['id']
