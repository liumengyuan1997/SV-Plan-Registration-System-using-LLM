from django.urls import path
from .views import SignUpView, SignInView, PublishEventView, ListEventView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('publishevent/', PublishEventView.as_view(), name='publish_event'),
    path('events/', ListEventView.as_view(), name='list_events'),
]
