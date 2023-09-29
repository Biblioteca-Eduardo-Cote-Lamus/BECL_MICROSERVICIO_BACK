from django.urls import path
from .views import CalendarEvents, SaveEvent

urlpatterns = [
    path('events_PDB/', CalendarEvents.as_view(), name='events_pdb'),
    path('schedule_PDB/', SaveEvent.as_view(), name='schedule_pdb'),
]
