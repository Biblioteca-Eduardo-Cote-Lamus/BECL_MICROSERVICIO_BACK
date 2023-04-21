from django.urls import path
from .views import events_PDB

urlpatterns = [
    path('events_PDB/', events_PDB, name='events_pdb')
]

