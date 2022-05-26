from django.urls import path
from .views import *

app_name = 'evaluator'

urlpatterns = [
    path('', ClassList.as_view(), name='class_list'),
    path('detail/<int:pk>/', ClassDetail.as_view(), name='class_detail'),
    path('create/', ClassCreate.as_view(), name='class_create'),
    path('students/', StudentList.as_view(), ),
    path('result/<int:pk>/', EvaluationResult.as_view(), name='result'),
    path('assignment/<int:pk>/', AssignmentNotice.as_view(), name='assignment_notice'),
    path('assignment/<int:assignment_pk>/submit/', SubmissionCreate.as_view(), name='submission_create'),
]
