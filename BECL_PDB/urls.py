from django.urls import path
from .views import schedule_PDB, download_document, CalendarEvents

urlpatterns = [
    path('events_PDB/', CalendarEvents.as_view(), name='events_pdb'),
    path('schedule_PDB/', schedule_PDB, name='schedule_pdb'),
    path('download/', download_document, name='download_document')
]
