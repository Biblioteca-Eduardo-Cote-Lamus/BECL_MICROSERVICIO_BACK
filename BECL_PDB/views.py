from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .models import Events_DB, Events_P
from datetime import datetime, timedelta
from docxtpl import DocxTemplate
from dotenv import load_dotenv
import os
import os.path
import jwt
import json
import pytz

list_events = []
list_hours_today = [6,7,8,9,10,11,12,13,14,15,16,17,18,19]

@csrf_exempt
@require_http_methods(['POST'])
def events_PDB(request):
    credentials = getCredentials()
    body = json.loads(request.body.decode('utf-8'))
    token = body.get('token')
    date = body.get('dates')
    type_event = body.get('type')
    service = build('calendar', 'v3', credentials=credentials)
    try:
        if not is_Token_Valid(token):
            list_event_today = events_today(service,date[0],date[1],type_event)
            hours_events = realization_events(list_event_today)
            hours_events_24H = stringToInt(hours_events)
            list_possible_hours = possible_hours(hours_events_24H,list_hours_today.copy())
            ranges = generate_ranges(list_possible_hours)
            print(ranges)
            answer = generate_possible_end_times(ranges)
            return JsonResponse({'events_hours':answer, 'events':list_event_today})     
        return JsonResponse({'ok': False, 'message':'Ocurrio un error'})
    except jwt.exceptions.InvalidTokenError:
        return JsonResponse({'ok': False})

@csrf_exempt
@require_http_methods(['POST'])
def schedule_PDB(request):
    body = json.loads(request.body.decode('utf-8'))
    token = body.get('token')
    title = body.get('title')
    dates = body.get('dates')
    emails = body.get('emails')
    types = body.get('type')
    try:
        if not is_Token_Valid(token):    
            credentials = getCredentials()
            event = format_event(title, dates, emails)
            service = build('calendar', 'v3', credentials=credentials)
            service.events().insert(calendarId='primary', body=event).execute()
            if types != 'BD':
                name =  get_format_document_A("Prueba xd", "Andres", "1152231", "Ingenieria", dates[0], dates[1], "100") if types == 'A' else get_format_document_S("GIA",'Biblioteca','3219172041','50','Andres Silva','7410',dates[0], dates[1])
                file_id = upload_to_folder(name, types)
                return JsonResponse({'ok': True,'message': '¡El evento fue agendado con exito!', 'urlFile': file_id, 'fileName':name})
            return JsonResponse({'ok': True, 'message': 'Evento agendado'})
        return JsonResponse({'ok': False,'message': '¡Ocurrio un error!'})
    except jwt.exceptions.ExpiredSignatureError:
        return JsonResponse({'ok': False,'message': '!El evento no se pudo agendar¡'})
#Funcion la cual crea el documento de apartado del auditorio
def get_format_document_A(title, name, code, dependence, start, end, num_people):
    doc = DocxTemplate('BECL_PDB/doc/formato auditorio.docx')
    now = datetime.utcnow()
    
    hour = now.strftime('%H-%M-%S')
    date = now.strftime('%d-%m-%Y')
    data_docx = {
        'fecha': date,
        'titulo': title,
        'dependencia': dependence,
        'personas': num_people,
        'nombre': name,
        'codigo': code,
        'inicio': start,
        'fin': end,
    }
    
    name_docx = f'{hour} Prestamo Auditorio.docx'
    doc.render(data_docx)
    doc.save(f'BECL_PDB/doc/doc_auditorio/{name_docx}')
    
    return name_docx

#Funcion la cual crea el documento de apartado de la sala de semilleros
def get_format_document_S(hotbed, department, phone, num_people, name, code, start, end):
    doc = DocxTemplate('BECL_PDB/doc/Formato semilleros.docx')
    now = datetime.utcnow()
    
    hour = now.strftime('%H-%M-%S')
    date = now.strftime('%d-%m-%Y')
    data_docx = {
        'fecha': date,
        'semillero': hotbed,
        'departamento': department,
        'telefono': phone,
        'personas': num_people,
        'nombre': name,
        'codigo': code,
        'inicio': start,
        'fin': end,
    }
    
    name_docx = f'{hour} Prestamo Semillero.docx'
    doc.render(data_docx)
    doc.save(name_docx)
    
    return name_docx

#Funcion que me retorna el formato en el cual tengo que mandar el evento a agendar
def format_event(title,dates,emails):
    list_emails = get_list_emails(emails)
    start = dates[0]
    end = dates[1]
    event = {
        'summary': title,
        'location': '',
        'description': 'probando',
        'start': {
            'dateTime': start,
            'timeZone': 'America/Bogota',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'America/Bogota',
        },
        'attendees': list_emails,
        'reminders': {
            'useDefault': False,
        },
    }
    return event

#Funcion que sube los formatos de prestamo a una carpeta de drive
def upload_to_folder(name_docx, option,data):
    load_dotenv()
    credentials = getCredentials()
    try:
        service = build('drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': f'Formato Auditorio {data["title"] - data["code"]}.docx' if option == 'A' else f'Formato Semillero {hour}.docx',
            'parents': [os.getenv('FOLDER_ID_A') if option == 'A' else os.getenv('FOLDER_ID_S')]
        }
        media = MediaFileUpload(f'BECL_PDB/doc/doc_auditorio/{name_docx}', mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields= 'id').execute()
        permission = {
            'type': 'anyone',
            'role': 'reader',
            'withLink': True
        }
        
        service.permissions().create(fileId=file.get('id'), body=permission).execute()
        return service.files().get(fileId=file['id'], fields='webViewLink').execute()['webViewLink']
    except HttpError:
        print('error aca en el httperror')
        return HttpResponse("ocurrio un error")

#Funcion que retorna la lista de correos en formato ({'email':'direccion de correo'})
def get_list_emails(emails):
    list_email = [{'email': 'andresalexanderss@ufps.edu.co'},
                  {'email': 'angelgabrielgara@ufps.edu.co'},]
    for email in emails:
        list_email.append({'email': email})
    return list_email

#Funcion que me retorna los eventos de una fecha dada
def events_today(service, start, end, option):
    events_result = service.events().list(calendarId='primary', timeMin=start, timeMax=end, singleEvents=True, orderBy='startTime').execute()
    list_events = events_result.get('items',[])
    list_events = list(filterByOption(list_events, option))
    return list_events

#Funcion que valida que el token este activo
def is_Token_Valid(token):
    colombia_time = datetime.utcnow() + timedelta(hours=-5)
    decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    exp_timestamp= decode_token['exp']
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    if colombia_time < exp_datetime:
        return False
    else:
        return True
    
#Funcion que me devuelve los eventos a realizar
def realization_events(list_event):
    list_hours_events = []
    for event in list_event:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        start_time = datetime.fromisoformat(start).strftime('%I:%M %p')
        end_time = datetime.fromisoformat(end).strftime('%I:%M %p')
        list_hours_events.append([start_time,end_time])
    return list_hours_events

#Funcion que convierte de unformato de Hora 00:00 PM/AM a formato de 24H
def stringToInt(list_hours):
    list_hours_int = []
    for hours in list_hours:
        start = datetime.strptime(hours[0], '%I:%M %p').strftime('%H')
        end = datetime.strptime(hours[1], '%I:%M %p').strftime('%H')
        list_hours_int.append([int(start), int(end)])
    return list_hours_int

#Funcion que me remueve las horas que no estan disponibles
def possible_hours(list_events, list_hours):
    for schedule in list_events:
        if len(schedule) == 0:
            return
        else:
            for hora in range(schedule[0], schedule[1]):
                list_hours.remove(hora)
    return list_hours

# Funcion que genera los posbles rangos de las horas
def generate_ranges(list_schedule):
    ranges = []
    if len(list_schedule) == 0: return ranges
    start_hours = list_schedule[0]
    if len(list_schedule) == 14:
        ranges.append([6,19])
        return ranges
    for i in range(len(list_schedule)-1):
        if list_schedule[i+1] - list_schedule[i] != 1:
            if start_hours == list_schedule[i]:
                ranges.append([start_hours])
            else:
                ranges.append([start_hours, list_schedule[i]])
            start_hours = list_schedule[i+1]
    ranges.append([start_hours, list_schedule[-1]])
    return ranges

#Funcion que genera los rangos de las horas: Ejemplo empieza a las 6 lo max es a las 10 tiempo de apartado de 4h
def generate_ranges_hours(start,end):
    max_possible_hours = start + 4
    if max_possible_hours in range(start, end +1):
        return {'hours': str(start) + ":00 am" if start <= 12 else str(abs(start-12)) + ":00 pm",
                'possible': [x for x in range(start+1, max_possible_hours+1)]}
    else:
        return {'hours': str(start) + ":00 am" if start <= 12 else str(abs(start-12)) + ":00 pm", 
                'possible': [x for x in range(start + 1, end + 2)]}

#Funcion que genera los rangos posibles si solo hay una hora
def generate_possible_end_times(ranges):
    hours = []
    for range_hours in ranges:
        lists = list(range(range_hours[0], range_hours[1] + 1)) if len(range_hours) == 2 else list(range(range_hours[0], range_hours[0] + 1))
        for i in lists:
            hours.append(generate_ranges_hours(i, range_hours[-1]))
    return hours

#Funcion para convertirla hora a entero
def getTimeToInt(time):
    pre_time = time[0:2]
    return int(pre_time[1]) if pre_time[0] == '0' else int(pre_time)

#Funcion que filtar los eventos por la opciones: A: Auditorio, S: semillero, BD: Base de datos
def filterByOption(events,option):
    print(events)
    return filter(lambda event: option in event['summary'][0] , events)

#Funcion que me genera el token
def getCredentials():
    # Si modifica este scopes, borra el archivo token.json 
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive']
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