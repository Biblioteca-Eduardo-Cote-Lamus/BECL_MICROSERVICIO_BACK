from django.urls import path
from .views import events_PDB, schedule_PDB, download_document

urlpatterns = [
    path('events_PDB/', events_PDB, name='events_pdb'),
    path('schedule_PDB/', schedule_PDB, name='schedule_pdb'),
    path('download/', download_document, name='download_document')
]
