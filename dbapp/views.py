from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, EventSerializer
from .models import User, Event
from .permission import IsAdminRole
from rest_framework.permissions import AllowAny
import base64
from django.utils.timezone import now


class SignUpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if password != user.password:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "role": user.role,
            "message": "Successful login",
        }, status=status.HTTP_200_OK)


class PublishEventView(APIView):

    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            try:
                event = serializer.save(event_published_by=request.user)
                print(event)
                return Response({
                    "success": True,
                    "message": "Event published successfully!",
                    "data": EventSerializer(event).data
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
    def get(self, request):
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
        events = Event.objects.all().order_by(sort_param)
        serialized_events = EventSerializer(events, many=True).data

        return Response({
            "success": True,
            "count": len(serialized_events),
            "events": serialized_events
        }, status=status.HTTP_200_OK)


class UpdateEventStatusView(APIView):
    def get(self, request):
        current_time = now()
        events = Event.objects.filter(event_status__in=["In process", "Overdue"])
        updated_events = 0
        for event in events:
            if current_time >= event.event_time:
                if event.event_status != "Overdue":
                    event.event_status = "Overdue"
                    event.save()
                    updated_events += 1
            else:
                if event.event_status != "In process":
                    event.event_status = "In process"
                    event.save()
                    updated_events += 1

        return Response({
            "success": True,
            "message": f"Event statuses updated successfully. {updated_events} events modified."
        }, status=status.HTTP_200_OK)