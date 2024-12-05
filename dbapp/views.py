from django.shortcuts import render, get_object_or_404, redirect
from .models import User, UploadedFile, Task, Event
from django.db import connection
from django.utils.timezone import now
from datetime import datetime
from .serializers import UploadedFileSerializer, SignupSerializer, EventSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permission import IsAdminRole
from rest_framework.permissions import AllowAny
import base64
from .utils import process_file_content, generate_task_description_and_due_date, task_detail_data, validate_date
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
import pytz
from datetime import datetime
from django.conf import settings
import json
import MySQLdb
import openai

openai.api_key = "sk-F26KW4HCJiSlbCfhR1XnyyKf11QnvbUN7lD0ZBYSgbT3BlbkFJs9TZ5gsij14tIJNLk_G__1-aEnKWzF4qA7V81-zGoA"


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role', 'Student')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        department = request.data.get('department', 'Khoury')

        if not email or not password or not role or not department:
            return Response(
                {"error": "Email, password, role, and department are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with connection.cursor() as cursor:
                check_email_sql = "SELECT 1 FROM dbapp_user WHERE email = %s"
                cursor.execute(check_email_sql, [email])
                if cursor.fetchone():
                    return Response(
                        {"error": "Email already exists."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                insert_sql = """
                    INSERT INTO dbapp_user (email, password, role, first_name, last_name, department, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(insert_sql, [email, password, role, first_name, last_name, department])

            return Response({"message": "success!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT role, password 
                    FROM dbapp_user 
                    WHERE email = %s
                """
                cursor.execute(query, [email])
                user = cursor.fetchone()

                if not user:
                    return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

                db_password, role = user[1], user[0]

                if password != db_password:
                    return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

                return Response({
                    "role": role,
                    "message": "Successful login",
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "An unexpected error occurred.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublishEventView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                event_name = data.get('event_name')
                event_description = data.get('event_description')
                event_location = data.get('event_location')
                event_time = data.get('event_time')
                event_status = data.get('event_status', 'Upcoming')
                event_category = data.get('event_category')
                event_published_by = request.user.email 

                insertion_sql = """
                    INSERT INTO dbapp_event 
                    (event_name, event_description, event_location, event_time, 
                     event_status, event_category, event_published_by, event_created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """

                params = (
                    event_name,
                    event_description,
                    event_location,
                    event_time,
                    event_status,
                    event_category,
                    event_published_by
                )

                with connection.cursor() as cursor:
                    cursor.execute(insertion_sql, params)

                    event_id_query = "SELECT LAST_INSERT_ID();"
                    cursor.execute(event_id_query)
                    event_id = cursor.fetchone()[0]

                    student_query = """
                        SELECT email FROM dbapp_user WHERE role = 'Student';
                    """
                    cursor.execute(student_query)
                    students = cursor.fetchall()

                    if students:
                        student_event_insertion_sql = """
                            INSERT INTO dbapp_studentevent (student_id, event_id, event_status, updated_at)
                            VALUES (%s, %s, 'Upcoming', NOW())
                        """
                        student_event_params = [
                            (student[0], event_id) for student in students
                        ]
                        cursor.executemany(student_event_insertion_sql, student_event_params)

                return Response({
                    "success": True,
                    "message": "Event published successfully!",
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class ListEventView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        auth_email = getattr(request, 'auth_email', None)
        if not auth_email:
            return Response({
                "success": False,
                "message": "Authentication email is required."
            }, status=status.HTTP_400_BAD_REQUEST)


        user_role = self.get_user_role(auth_email)
        if not user_role:
            return Response({
                "success": False,
                "message": "User role not found. Please contact admin."
            }, status=status.HTTP_404_NOT_FOUND)


        self.update_event_status()


        sort_param = request.query_params.get('sort', 'event_time')
        valid_sort_fields = [
            'event_time', '-event_time',
            'event_published_by', '-event_published_by',
            'event_created_at', '-event_created_at'
        ]

        if sort_param not in valid_sort_fields:
            return Response({
                "success": False,
                "message": f"Invalid sort parameter. Must be one of {valid_sort_fields}."
            }, status=status.HTTP_400_BAD_REQUEST)

        order_param = sort_param.lstrip('-')
        order = 'DESC' if sort_param.startswith('-') else 'ASC'


        if user_role == 'Admin':
            select_sql = f"""
                SELECT 
                    e.event_id, 
                    e.event_name, 
                    e.event_description, 
                    e.event_location, 
                    e.event_time, 
                    e.event_category, 
                    e.event_published_by, 
                    e.event_created_at,
                    e.event_status
                FROM dbapp_event AS e
                ORDER BY {order_param} {order}
            """
            query_params = [] 
        else:
            select_sql = f"""
                SELECT 
                    e.event_id, 
                    e.event_name, 
                    e.event_description, 
                    e.event_location, 
                    e.event_time, 
                    e.event_category, 
                    e.event_published_by, 
                    e.event_created_at,
                    se.event_status
                FROM dbapp_studentevent AS se
                INNER JOIN dbapp_event AS e ON se.event_id = e.event_id
                WHERE se.student_id = %s
                ORDER BY {order_param} {order}
            """
            query_params = [auth_email]


        try:
            with connection.cursor() as cursor:
                cursor.execute(select_sql, query_params)
                rows = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            events = [dict(zip(columns, row)) for row in rows]

            return Response({
                "success": True,
                "events": events
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while fetching events.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_event_status(self):
        current_time = now()
        print(f"Updating statuses at {current_time}")

        update_student_sql = """
            UPDATE dbapp_studentevent AS se
            INNER JOIN dbapp_event AS e ON se.event_id = e.event_id
            SET se.event_status = 'Overdue', e.event_status = 'Overdue'
            WHERE se.event_status NOT IN ('Overdue', 'Attended')
            AND e.event_time <= %s
        """

        update_event_sql = """
            UPDATE dbapp_event
            SET event_status = 'Overdue'
            WHERE event_status NOT IN ('Overdue', 'Attended')
            AND event_time <= %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(update_student_sql, [current_time])
                print(f"{cursor.rowcount} student events updated to 'Overdue'")

                cursor.execute(update_event_sql, [current_time])
                print(f"{cursor.rowcount} standalone events updated to 'Overdue'")
        except Exception as e:
            print(f"Error updating event statuses: {str(e)}")




    def get_user_role(self, email):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT role FROM dbapp_user WHERE email = %s", [email]
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Error fetching user role: {str(e)}")
            return None


class FilterEventByCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        auth_email = getattr(request, 'auth_email', None)
        if not auth_email:
            return Response({
                "success": False,
                "message": "Authentication email is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        event_categories = request.query_params.getlist('category', None)
        event_status = request.query_params.get('status', None)
        start_time = request.query_params.get('start_time', None)
        end_time = request.query_params.get('end_time', None)

        if event_status:
            event_status = event_status.capitalize().strip()

        valid_statuses = ['Upcoming', 'Attended', 'Overdue']

        if event_status and event_status not in valid_statuses:
            return Response({
                "success": False,
                "message": f"Invalid status parameter. Must be one of {valid_statuses}."
            }, status=status.HTTP_400_BAD_REQUEST)

        filters = []
        params = []

        filters.append("se.student_id = %s")
        params.append(auth_email)

        if event_categories:
            filters.append(f"e.event_category IN ({','.join(['%s'] * len(event_categories))})")
            params.extend(event_categories)


        if event_status:
            filters.append("se.event_status = %s")
            params.append(event_status)

        try:
            if start_time:
                start_time = parse_datetime(start_time)
                if not start_time:
                    raise ValueError("Invalid start_time format.")
                start_time = start_time.astimezone(pytz.UTC)
                filters.append("e.event_time >= %s")
                params.append(start_time)

            if end_time:
                end_time = parse_datetime(end_time)
                if not end_time:
                    raise ValueError("Invalid end_time format.")
                end_time = end_time.astimezone(pytz.UTC)
                filters.append("e.event_time <= %s")
                params.append(end_time)

            if start_time and end_time and start_time > end_time:
                return Response({
                    "success": False,
                    "message": "Invalid time range: start_time must be earlier than end_time."
                }, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response({
                "success": False,
                "message": "Invalid time format. Use ISO 8601 format (e.g., '2024-11-01T00:00:00').",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        filter_query = " AND ".join(filters)

        query = f"""
            SELECT 
                e.event_id, 
                e.event_name, 
                e.event_description, 
                e.event_location, 
                e.event_time, 
                e.event_category, 
                e.event_published_by, 
                e.event_created_at,
                se.event_status
            FROM dbapp_studentevent AS se
            INNER JOIN dbapp_event AS e ON se.event_id = e.event_id
            WHERE {filter_query}
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            events = [dict(zip(columns, row)) for row in rows]

            return Response({
                "success": True,
                "count": len(events),
                "events": EventSerializer(events, many=True).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while filtering events.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateEventStatusView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, event_id):
        current_time = now()
        print(f"Current Time (UTC): {current_time}")

        auth_email = getattr(request, 'auth_email', None)
        if not auth_email:
            return Response({
                "success": False,
                "message": "Authentication email is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        new_status = request.data.get('status', None)
        VALID_STATUSES = ['Upcoming', 'Attended', 'Overdue', 'Unattended']

        if not new_status:
            return Response({
                "success": False,
                "message": "Status is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        new_status = new_status.capitalize().strip()
        print(f"Received status: {new_status}")

        if new_status == 'Unattended':
            new_status = 'Upcoming'

        if new_status not in VALID_STATUSES:
            return Response({
                "success": False,
                "message": f"Invalid status. Must be one of {VALID_STATUSES}."
            }, status=status.HTTP_400_BAD_REQUEST)

        update_sql = """
            UPDATE dbapp_studentevent
            SET event_status = %s, updated_at = %s
            WHERE student_id = %s AND event_id = %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [new_status, current_time, auth_email, event_id])
                if cursor.rowcount == 0:
                    return Response({
                        "success": False,
                        "message": f"No event found for the current user with event_id {event_id}."
                    }, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "success": True,
                "message": f"Your event status has been updated to '{new_status}'."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return Response({
                "success": False,
                "message": "An unexpected error occurred. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileUploadAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, student_email):
        user = get_object_or_404(User, email=student_email)
        serializer = UploadedFileSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = request.FILES['file']
            content_type = uploaded_file.content_type

            uploaded_file = serializer.save()
            file = uploaded_file.file

            # Process the uploaded file content
            content = process_file_content(file, content_type)
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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

        print(task_name)
        print(due_date)
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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


class GenerateSQLView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            user_input = request.data.get("user_input")
            auth_email = getattr(request, 'auth_email', None)
            print(request.data)
            print(auth_email)
            if not user_input:
                return Response({"error": "'user_input' is required."}, status=status.HTTP_400_BAD_REQUEST)

            schema = self.get_database_schema()

            prompt = f"""
            The database schema is as follows:
            {schema}

            The user has provided the following requirement: "{user_input}".

            Generate a valid SQL query based on the user's requirement and provided schema. Use plain text formatting without any escaped characters like \\". I want a sql query which I just need to copy it, then I can run it. If an email is needed, please refer to the current email: "{auth_email}". Return only the SQL query as a single line, no explanations.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert SQL assistant."},
                    {"role": "user", "content": prompt},
                ],
                timeout=120
            )
            sql_query = response['choices'][0]['message']['content'].strip()

            return Response({"sql_query": sql_query}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_database_schema(self):
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            schema = {}
            for (table_name,) in tables:
                cursor.execute(f"DESCRIBE {table_name};")
                columns = cursor.fetchall()
                schema[table_name] = [{"Field": col[0], "Type": col[1]} for col in columns]

            return schema
        except Exception as e:
            raise Exception(f"Error fetching schema: {e}")


class ExecuteSQLView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            sql_query = request.data.get("sql_query")
            if not sql_query:
                return Response({"error": "'sql_query' is required."}, status=status.HTTP_400_BAD_REQUEST)

            execution_result = self.execute_sql(sql_query)
            return Response({"result": execution_result}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def execute_sql(self, sql_query):
        try:
            print(sql_query)
            cursor = connection.cursor()

            cursor.execute(sql_query)
            if sql_query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                result = [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
            else:
                connection.commit()
                result = {"message": "Query executed successfully."}

            cursor.close()
            connection.close()
            return result

        except Exception as e:
            print(e)
            raise Exception(f"Error executing SQL query: {e}")
