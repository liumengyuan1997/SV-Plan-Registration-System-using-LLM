from django.contrib import admin
from django.urls import path
from dbapp import views
from django.urls import include, path

urlpatterns = [
    path('upload/<str:student_email>', views.FileUploadAPIView.as_view(), name='upload_file'),
    path('task/<str:student_email>/<int:task_id>', views.TaskDetailAPIView.as_view(), name='task_detail'),
    path('task/update/<str:studentEmail>/<int:task_id>', views.UpdateTaskAPIView.as_view(), name='update_task'),
    path('tasks/<studentEmail>', views.AllTasksAPIView.as_view(), name='all_tasks'),
    path('tasks/sort-due-date/<studentEmail>', views.SortTasksByDueDateAPIView.as_view(), name='sort_due_date'),
    path('tasks/sort-entry-date/<studentEmail>', views.SortTasksByEntryDateAPIView.as_view(), name='sort_entry_date'),
    path('tasks/filter-tasks/<studentEmail>', views.FilterTaskByCategoryView.as_view(), name='filter_tasks'),
    path("admin/", admin.site.urls),
    path('api/', include('dbapp.urls'))
]
