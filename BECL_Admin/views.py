from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from BECL_PDB.models import Eventos
from BECL_PDB.views import is_Token_Valid
from .serializers import EventosSerializers
import jwt
import json

@csrf_exempt
@api_view(["GET"])
def get_list_events_to_accept(request):
    if request.method == "GET":
        list_events = Eventos.objects.filter(estado__por_revisar=True)
        event_serializers = EventosSerializers(list_events, many=True)
        return Response(event_serializers.data)
    
@csrf_exempt
@api_view(["PUT"])
def approve_event(request):
    body = json.loads(request.body.decode('utf-8'))
    header = request.META
    token = request.header.get('Authorization')
    state = body.get('state')
    pk = body.get('id_event')

    try:
        if not is_Token_Valid(token):
            event = Eventos.objects.filter(id=pk).first()
            if event:
                event.estado.aceptado = state
                event_serializers = EventosSerializers(event)
    except jwt.exceptions.ExpiredSignatureError:
        return Response({'message':'Token Expirado'}, status= status.HTTP_400_BAD_REQUEST)
    
    
# Usando DRF

class Listar_por_Estado(APIView):
    
    def get(self, request ):
        pass
    