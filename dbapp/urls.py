from django.urls import path
from .views import SignUpView, SignInView, PublishEventView, ListEventView, FilterEventByCategoryView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('publish-event/', PublishEventView.as_view(), name='publish_event'),
    path('list-events/', ListEventView.as_view(), name='list_events'),
    path('filter-events/', FilterEventByCategoryView.as_view(), name='filter_events'),
]
