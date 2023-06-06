from django.urls import path
from .views import get_list_events_to_accept, approve_event

urlpatterns = [
    path('list-events', get_list_events_to_accept, name='list_events'),
    path('approve-event/', approve_event, name='approve_event'),
]
