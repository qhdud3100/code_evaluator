from django.contrib import admin

# Register your models here.
from evaluator.models import Classroom, Assignment, Submission

@admin.register(Classroom)
class Classroom(admin.ModelAdmin):

    list_display = ['name']

@admin.register(Assignment)
class Assignment(admin.ModelAdmin):

    list_display = ['name']

@admin.register(Submission)
class Submission(admin.ModelAdmin):

    list_display = ['assignment']
