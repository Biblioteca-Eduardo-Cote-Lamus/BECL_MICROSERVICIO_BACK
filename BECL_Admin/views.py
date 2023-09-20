from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from django.conf import settings
from BECL_PDB.models import Eventos
from BECL_PDB.views import is_Token_Valid, getCredentials, format_event, get_general_document, upload_to_folder, sendEmialEvent
from .serializers import EventosSerializers
import jwt
import json

@csrf_exempt
@api_view(["GET"])
def get_list_events_to_accept(request):
    filterId = request.GET.get('filterId')
    if filterId is None: 
        filterId = 1
    event_serializers = EventosSerializers(Eventos.objects.filter(estado_id=filterId), many=True)
    return Response(event_serializers.data)
    
@csrf_exempt
@api_view(["PUT"])
def approve_event(request):
    body = json.loads(request.body.decode('utf-8'))
    token = request.headers.get('Authorization')
    state = int(body.get('state'))
    pk = int(body.get('id_event'))
    credentials = getCredentials()

    try:
        #Decodificamos el token para obtener el rol del usuario
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # print(payload)
        rol = payload['user_rol']
        #Se extrae el evento que me estan solicitando
        event = Eventos.objects.get(id=pk)
        event.estado_id = state
        event.save()
        #Validamos el token y Si el rol es el de Administrador
        if not is_Token_Valid(token) and rol == "Administrador":
        #Si el estado es 2, es por que fue aceptado
            if (state == 2):
                #se genera el evento. Se extrae el titulo, fechas (Inicio y Fin), emails y el tipo de evento.
                calendar_event = format_event(event.titulo, event.fecha, event.inicio, event.final, eval(event.encargados))
                # print(calendar_event)
                service = build('calendar', 'v3', credentials=credentials)
                #Se agenda el evento
                service.events().insert(calendarId='primary', body=calendar_event).execute()
                # para generar el formato debe de ser diferente a BD el type enviado en la request
                if (event.tipo != "DB"):
                    #Generamos el doc de soporte del prestamo
                    name_doc = get_general_document(event.fecha, event.titulo, event.dependencia, event.cantidad_personas, event.usuario.nombre, event.usuario.codigo
                                                    , event.inicio, event.final, event.tipo)
                    #Guardamos en una carpeta de drive el soporte
                    save_folder = upload_to_folder(name_doc, event.tipo, credentials)
                    hours = (event.inicio,event.final)
                    #Se envia un correo informando sobre el evento y el comprobante del mismo
                    sendEmialEvent(event.fecha, hours, eval(event.encargados), event.tipo, name_doc)
                    return Response({'ok':True, 'message':'Evento Agendado'}, status=status.HTTP_200_OK)
                #Se envia un correo informando de la capacitacion a realiar 
                sendEmialEvent(event.fecha, hours, event.encargados, event.tipo)
                service.close()
                return Response({'ok':True,'message':"Capacitacion Agendada"}, status=status.HTTP_200_OK)
        #Si el estado es 3, es por que fue rechazado
        return Response({'ok':True,'message':"El evento fue rechazado."}, status=status.HTTP_200_OK)
    except jwt.exceptions.ExpiredSignatureError:
        return Response({"ok":False,'message':'Token Expirado'}, status= status.HTTP_400_BAD_REQUEST)