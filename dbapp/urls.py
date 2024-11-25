from django.urls import path
from .views import SignUpView, SignInView, PublishEventView, ListEventView, FilterEventByCategoryView, UpdateEventStatusView, GenerateSQLView, ExecuteSQLView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('publish-event/', PublishEventView.as_view(), name='publish_event'),
    path('list-events/', ListEventView.as_view(), name='list_events'),
    path('filter-events/', FilterEventByCategoryView.as_view(), name='filter_events'),
    path('update-event-status/<int:event_id>/status', UpdateEventStatusView.as_view(), name='update_event_status'),
    path('generate-sql/', GenerateSQLView.as_view(), name='generate_sql'),
    path('execute-sql/', ExecuteSQLView.as_view(), name='execute_sql'),
]
