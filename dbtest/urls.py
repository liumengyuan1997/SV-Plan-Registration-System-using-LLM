"""
URL configuration for dbtest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from dbapp import views

urlpatterns = [
    path('upload/<str:student_email>', views.FileUploadAPIView.as_view(), name='upload_file'),
    path('task/<str:student_email>/<int:task_id>', views.TaskDetailAPIView.as_view(), name='task_detail'),
    path('task/update/<studentEmail>/<int:task_id>', views.UpdateTaskAPIView.as_view(), name='update_task'),
    path('tasks/<studentEmail>', views.AllTasksAPIView.as_view(), name='all_tasks'),
    path('tasks/sort-due-date/<studentEmail>', views.SortTasksByDueDateAPIView.as_view(), name='sort_due_date'),
    path('tasks/sort-entry-date/<studentEmail>', views.SortTasksByEntryDateAPIView.as_view(), name='sort_entry_date'),
    path('tasks/filter-tasks/<studentEmail>', views.FilterTaskByCategoryView.as_view(), name='filter_tasks')
]
