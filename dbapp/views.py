from django.shortcuts import render, get_object_or_404, redirect
from .models import User, UploadedFile, Task
from django.db import connection
from django.utils.timezone import now
from datetime import datetime
from .serializers import UploadedFileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils import process_file_content, generate_task_description_and_due_date, task_detail_data, validate_date

class FileUploadAPIView(APIView):
    def post(self, request, student_email):
        user = get_object_or_404(User, email=student_email)
        serializer = UploadedFileSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.save()
            file = uploaded_file.file

            # Process the uploaded file content
            content = process_file_content(file)
            if content:
                task_name, task_description, due_date = generate_task_description_and_due_date(content)

                # Create a new task
                task = Task.objects.create(
                    studentEmail=user,
                    taskName = task_name,
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
                        'taskName': task.taskName,
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
    def get(self, request, student_email, task_id):
        # Retrieve the task
        task = get_object_or_404(Task, pk=task_id, studentEmail=student_email)

        # Retrieve the associated file (if any)
        uploaded_file = UploadedFile.objects.filter(taskId=task).first()

        # Prepare the response data
        response_data = {
            'taskId': task.taskId,
            'taskName': task.taskName,
            'description': task.description,
            'entryDate': task.entryDate,
            'dueDate': task.dueDate,
            'taskStatus': task.taskStatus,
            'taskCategory': task.taskCategory,
            'file': None if not uploaded_file else {
                'fileId': uploaded_file.fileId,
                'filePath': uploaded_file.file.url
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

class UpdateTaskAPIView(APIView):
    def post(self, request, *args, **kwargs):
        student_email = kwargs.get('studentEmail')  # Correct key is based on URL
        task_id = kwargs.get('task_id')
        user = get_object_or_404(User, email=student_email)
        # Get the task object or return a 404 error if not found
        task = get_object_or_404(Task, pk=task_id, studentEmail=user)

        # Extract fields from the JSON request body
        task_name = request.data.get('taskName')
        description = request.data.get('description')
        due_date = request.data.get('dueDate')
        task_status = request.data.get('taskStatus')
        task_category = request.data.get('taskCategory')

        if task_name:
            task.taskName = task_name

        if description:
            task.description = description
        
        if due_date:
            try:
                task.dueDate = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if task_status:
            task.taskStatus = task_status
        
        if task_category:
            task.taskCategory = task_category

        task.save()

        # Return the updated task data as a JSON response
        return Response({
            'taskId': task.taskId,
            'taskName': task.taskName,
            'description': task.description,
            'dueDate': task.dueDate,
            'studentEmail': task.studentEmail.email,
            'entryDate': task.entryDate,
            'taskStatus': task.taskStatus,
            'taskCategory': task.taskCategory
        }, status=status.HTTP_200_OK)

class AllTasksAPIView(APIView):
    def get(self, request, studentEmail):
        if not studentEmail:
            return Response({
                "success": False,
                "message": "The 'studentEmail' parameter is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=studentEmail)
        # Retrieve all tasks
        tasks = Task.objects.filter(studentEmail=user)

        # Use the helper function to prepare detailed task data
        tasks_data = [task_detail_data(task.taskId) for task in tasks]

        return Response({'tasks': tasks_data}, status=status.HTTP_200_OK)

class SortTasksByDueDateAPIView(APIView):
    def get(self, request, studentEmail):
        # Get the sorting order from query parameters
        order = request.GET.get('order', 'asc').lower()

        # Determine the sorting field based on the order
        order_field = '-dueDate' if order == 'desc' else 'dueDate'

        # Query the tasks sorted by the determined order
        tasks = Task.objects.filter(studentEmail=studentEmail).order_by(order_field)

        # Use the helper function to prepare detailed task data
        tasks_data = [task_detail_data(task.taskId) for task in tasks]

        return Response({'tasks': tasks_data}, status=status.HTTP_200_OK)

class SortTasksByEntryDateAPIView(APIView):
    def get(self, request, studentEmail):
        # Get the sorting order from query parameters
        order = request.GET.get('order', 'asc').lower()

        # Determine the sorting field based on the order
        order_field = '-entryDate' if order == 'desc' else 'entryDate'

        # Query the tasks sorted by the determined order
        tasks = Task.objects.filter(studentEmail=studentEmail).order_by(order_field)

        # Use the helper function to prepare detailed task data
        tasks_data = [task_detail_data(task.taskId) for task in tasks]

        return Response({'tasks': tasks_data}, status=200)

class FilterTaskByCategoryView(APIView):
    def get(self, request, studentEmail):
        task_name = request.query_params.get('taskName', None)
        entry_date = validate_date(request.query_params.get('entryDate', None))
        due_date = validate_date(request.query_params.get('dueDate', None))
        task_status = request.query_params.get('taskStatus', None)
        task_category = request.query_params.getlist('taskCategory', None)

        filters = []
        params = []

        user = get_object_or_404(User, email=studentEmail)
        filters.append("email = %s")
        params.append(user.email)

        if task_name:
            filters.append("taskName = %s")
            params.append(task_name)
        
        if entry_date:
            filters.append("entryDate = %s")
            params.append(entry_date)
        
        if due_date:
            filters.append("dueDate = %s")
            params.append(due_date)

        if task_status:
            filters.append("taskStatus = %s")
            params.append(task_status)

        if task_category:
            filters.append("taskCategory = %s")
            params.append(task_category)

        if not filters:
            return Response({
                "success": False,
                "message": "No filtering parameters provided. At least one of 'taskStatus', 'entryDate', or 'taskCategory' is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        filter_query = " AND ".join(filters)

        query = f"""
            SELECT
                taskName, 
                email AS studentEmail, 
                entryDate, 
                dueDate, 
                taskStatus, 
                taskCategory
            FROM tasks 
            WHERE {filter_query}
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                columns = [col[0] for col in cursor.description]

                tasks = [dict(zip(columns, row)) for row in rows]

            return Response({
                "success": True,
                "count": len(tasks),
                "tasks": tasks
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while filtering tasks.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)