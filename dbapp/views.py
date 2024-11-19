from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

from .models import UploadedFile, Task
from django.db import connection
from django.utils.timezone import now
from datetime import datetime
from .serializers import UploadedFileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils import process_file_content, generate_task_description_and_due_date, task_detail_data

class FileUploadAPIView(APIView):
    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.save()
            file = uploaded_file.file

            # Process the uploaded file content
            content = process_file_content(file)
            if content:
                task_description, due_date = generate_task_description_and_due_date(content)

                # Create a new task
                task = Task.objects.create(
                    studentId=None,  # TODO: After adding a student table
                    description=task_description,
                    entryDate=now().date(),
                    dueDate=due_date
                )

                # Link the uploaded file to the created task
                uploaded_file.taskId = task
                uploaded_file.save()

                return Response({
                    'message': 'Task and file created successfully.',
                    'task': {
                        'taskId': task.taskId,
                        'description': task.description,
                        'entryDate': task.entryDate,
                        'dueDate': task.dueDate
                    },
                    'file': {
                        'fileId': uploaded_file.fileId,
                        'filePath': uploaded_file.file.url
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailAPIView(APIView):
    def get(self, request, task_id):
        # Retrieve the task
        task = get_object_or_404(Task, pk=task_id)
        
        # Retrieve the associated file (if any)
        uploaded_file = UploadedFile.objects.filter(taskId=task).first()

        # Prepare the response data
        response_data = {
            'taskId': task.taskId,
            'description': task.description,
            'entryDate': task.entryDate,
            'dueDate': task.dueDate,
            'file': None if not uploaded_file else {
                'fileId': uploaded_file.fileId,
                'filePath': uploaded_file.file.url
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

class UpdateTaskAPIView(APIView):
    def post(self, request, task_id):
        # Get the task object or return a 404 error if not found
        task = get_object_or_404(Task, pk=task_id)

        # Extract fields from the JSON request body
        description = request.data.get('description')
        due_date = request.data.get('dueDate')

        # Update description if provided
        if description:
            task.description = description
        
        # Update due date if provided and valid
        if due_date:
            try:
                task.dueDate = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the updated task
        task.save()

        # Return the updated task data as a JSON response
        return Response({
            'taskId': task.taskId,
            'description': task.description,
            'dueDate': task.dueDate,
            'studentId': task.studentId,
            'entryDate': task.entryDate,
        }, status=status.HTTP_200_OK)

class AllTasksAPIView(APIView):
    def get(self, request):
        # Retrieve all tasks
        tasks = Task.objects.all()

        # Use the helper function to prepare detailed task data
        tasks_data = [task_detail_data(task.taskId) for task in tasks]

        return Response({'tasks': tasks_data}, status=status.HTTP_200_OK)

class SortTasksByDueDateAPIView(APIView):
    def get(self, request):
        # Get the sorting order from query parameters
        order = request.GET.get('order', 'asc').lower()

        # Determine the sorting field based on the order
        order_field = '-dueDate' if order == 'desc' else 'dueDate'

        # Query the tasks sorted by the determined order
        tasks = Task.objects.order_by(order_field)

        # Use the helper function to prepare detailed task data
        tasks_data = [task_detail_data(task.taskId) for task in tasks]

        return Response({'tasks': tasks_data}, status=status.HTTP_200_OK)

class SortTasksByEntryDateAPIView(APIView):
    def get(self, request):
        # Get the sorting order from query parameters
        order = request.GET.get('order', 'asc').lower()

        # Determine the sorting field based on the order
        order_field = '-entryDate' if order == 'desc' else 'entryDate'

        # Query the tasks sorted by the determined order
        tasks = Task.objects.order_by(order_field)

        # Use the helper function to prepare detailed task data
        tasks_data = [task_detail_data(task.taskId) for task in tasks]

        return Response({'tasks': tasks_data}, status=200)