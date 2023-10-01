from django.urls import path
from .views import ListEvents, ApproveEvent

urlpatterns = [
    path('list-events', ListEvents.as_view(), name='list_events'),
    path('approve-event/', ApproveEvent.as_view(), name='approve_event_v2'),
]
