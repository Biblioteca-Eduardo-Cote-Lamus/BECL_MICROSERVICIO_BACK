from django.urls import path
from .views import events_PDB, schedule_PDB

urlpatterns = [
    path('events_PDB/', events_PDB, name='events_pdb'),
    path('schedule_PDB/', schedule_PDB, name='schedule_pdb')
]

