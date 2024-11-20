from django.utils.timezone import now
from .models import Event

class UpdateEventStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.update_event_status()
        response = self.get_response(request)
        return response

    def update_event_status(self):
        current_time = now()

        events_to_update = Event.objects.filter(event_time__lte=current_time).exclude(event_status="Overdue")

        for event in events_to_update:
            event.event_status = "Overdue"

        Event.objects.bulk_update(events_to_update, ['event_status'])
