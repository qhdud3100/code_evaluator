from django.urls import path
from .views import *

app_name = 'evaluator'

urlpatterns = [
    path('', ClassList.as_view(), name='class_list'),
    path('detail/<int:pk>/', ClassDetail.as_view(), name='class_detail'),
    path('create/', ClassCreate.as_view(), name='class_create'),
    path('students/', StudentList.as_view(), ),
    path('result/', EvaluationResult.as_view(), ),
    path('upload/', AssignmentUpload.as_view(), name='upload')
]
