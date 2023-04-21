from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
from .models import Events_DB, Events_P
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import jwt
import json

list_events = []

@csrf_exempt
@require_http_methods(['POST'])
def events_PDB(request):
    credentials = getCredentials()
    body = json.loads(request.body.decode('utf-8'))
    token = body.get('token')
    fechas = body.get('dates')
    service = build('calendar', 'v3', credentials=credentials)
    if is_Token_Valid(token):
        events_result = service.events().list(calendarId='primary', timeMin=fechas[0], timeMax=fechas[1], singleEvents=True, orderBy='startTime').execute()
        list_events = events_result.get('items', [])
        list_events = list( map(lambda event: event["summary"], list_events) )
        return JsonResponse({'evenst': list_events})

#Funcion que valida que el token este activo
def is_Token_Valid(token):
    try:
        decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        exp_timestamp= decode_token['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        if datetime.utcnow() > exp_datetime:
            return JsonResponse({'ok': False})
    except jwt.exceptions.InvalidSignatureError:
        return JsonResponse({'ok':False})

#Funcion que me devuelve los eventos a realizar
def realization_events(event):
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    start_time = datetime.fromisoformat(start).strftime('%I:%M %p')
    end_time = datetime.fromisoformat(end).strftime('%I:%M %p')
    return [start_time, end_time]

#Funcion que retorna el inicio del dia
def todayStart():
    return datetime.now(pytz.timezone('America/Bogota')).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

#Funcion que retorno el fin del dia
def todayEnd():
    return datetime.now(pytz.timezone('America/Bogota')).replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

#Funcion para convertirla hora a entero
def getTimeToInt(time):
    pre_time = time[0:2]
    return int(pre_time[1]) if pre_time[0] == '0' else int(pre_time)

#Funcion que filtar los eventos por la opciones: A: Auditorio, S: semillero, BD: Base de datos
def filterByOption(events,option):
    return filter(lambda event: option in event['summary'][0:3], events)

#Funcion que me genera el token
def getCredentials():
    # Si modifica este scopes, borra el archivo token.json 
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None
    # El archivo token.json almacena los tokens de acceso y actualización del usuario, y es
    # creado automáticamente cuando el flujo de autorización se completa por primera vez
    # tiempo.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Si no hay credenciales (válidas) disponibles, permita que el usuario inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds