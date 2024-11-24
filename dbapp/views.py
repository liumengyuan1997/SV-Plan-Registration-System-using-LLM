from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, EventSerializer
from .models import User, Event
from .permission import IsAdminRole
from rest_framework.permissions import AllowAny
import base64
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
import pytz
from datetime import datetime



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
                event_status = data.get('event_status', 'In process')
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

        select_sql = f"""
            SELECT 
                event_id, 
                event_name, 
                event_description, 
                event_location, 
                event_time, 
                event_status, 
                event_category, 
                event_published_by, 
                event_created_at 
            FROM dbapp_event 
            ORDER BY {order_param} {order}
        """

        with connection.cursor() as cursor:
            cursor.execute(select_sql)
            rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        events = [dict(zip(columns, row)) for row in rows]

        return Response({
            "success": True,
            "events": EventSerializer(events, many=True).data
        }, status=status.HTTP_200_OK)

    def update_event_status(self):
        current_time = now()

        update_sql = """
            UPDATE dbapp_event
            SET event_status = 'Overdue'
            WHERE event_status != 'Overdue' 
            AND event_status != 'Attended'
            AND event_time <= %s
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [current_time])
        except Exception as e:
            print(f"Error updating event statuses: {str(e)}")


class FilterEventByCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        event_categories = request.query_params.getlist('category', None) 
        event_status = request.query_params.get('status', None)
        start_time = request.query_params.get('start_time', None)
        end_time = request.query_params.get('end_time', None)



        print(start_time)

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

        if event_categories:
            filters.append(f"event_category IN ({','.join(['%s'] * len(event_categories))})")
            params.extend(event_categories)

 
        if event_status:
            filters.append("event_status = %s")
            params.append(event_status)

        try:
            if start_time:
                start_time = parse_datetime(start_time)
                if not start_time:
                    raise ValueError("Invalid start_time format.")
                start_time = start_time.astimezone(pytz.UTC) 
                start_time = start_time.strftime('%Y-%m-%d %H:%M:%S.%f')  
                filters.append("event_time >= %s")
                params.append(start_time)

            if end_time:
                end_time = parse_datetime(end_time)  
                if not end_time:
                    raise ValueError("Invalid end_time format.")
                end_time = end_time.astimezone(pytz.UTC)
                end_time = end_time.strftime('%Y-%m-%d %H:%M:%S.%f')  
                filters.append("event_time <= %s")
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



        if not filters:
            return Response({
                "success": False,
                "message": "At least one filtering parameter ('category' or 'status') is required."
            }, status=status.HTTP_400_BAD_REQUEST)


        filter_query = " AND ".join(filters)

        query = f"""
            SELECT 
                event_id, 
                event_name, 
                event_description, 
                event_location, 
                event_time, 
                event_status, 
                event_category, 
                event_published_by, 
                event_created_at 
            FROM dbapp_event 
            WHERE {filter_query}
        """

        print("sql: ", query)
        print("params: ", params)

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
        new_status = request.data.get('status', None)

        valid_statuses = ['Upcoming', 'Attended', 'Overdue', 'Unattended']

        if new_status:
            new_status = new_status.capitalize().strip() 

        if new_status == 'Unattended':
            new_status = 'Upcoming'

        print(f"Received event_status: {new_status}")


        if new_status not in valid_statuses:
            return Response({
                "success": False,
                "message": f"Invalid status. Must be one of {valid_statuses}."
            }, status=status.HTTP_400_BAD_REQUEST)

        update_sql = """
            UPDATE dbapp_event
            SET event_status = %s
            WHERE event_id = %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(update_sql, [new_status, event_id])

                if cursor.rowcount == 0:
                    return Response({
                        "success": False,
                        "message": f"No event found with id {event_id}."
                    }, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "success": True,
                "message": f"Event status updated to '{new_status}'."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while updating the event status.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


