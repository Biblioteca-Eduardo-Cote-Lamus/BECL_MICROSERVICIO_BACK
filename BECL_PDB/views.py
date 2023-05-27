from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import FileResponse, JsonResponse, HttpResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
from docxtpl import DocxTemplate
from dotenv import load_dotenv
import os
import os.path
import jwt
import json
from docx2pdf import convert

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
            list_possible_hours = possible_hours(list_event_today,list_hours_today.copy())
            ranges = generate_ranges(list_possible_hours)
            answer = generate_possible_end_times(ranges)
            service.close()
            return JsonResponse({'events_hours':answer})     
        return JsonResponse({'ok': False, 'message':'Ocurrio un error'})
    except jwt.exceptions.InvalidTokenError:
        return JsonResponse({'ok': False})

@csrf_exempt
@require_http_methods(['POST'])
def schedule_PDB(request):
    body = json.loads(request.body.decode('utf-8'))
    token = body.get('token')
    #se extrae toda la información del parametro data que se envia de la request. 
    calendar = body.get('data')['calendar']
    support = body.get('data')['support']
    try:
        if not is_Token_Valid(token):    
            credentials = getCredentials()
            #se genera el evento. Se extrae el titulo, fechas, emails y el tipo de evento.
            event = format_event(calendar['title'], calendar['dates'], calendar['emails'])
            service = build('calendar', 'v3', credentials=credentials)
            #se agenda el evento. 
            service.events().insert(calendarId='primary', body=event).execute()
            # para generar el formato debe de ser diferente a BD el type enviado en la request
            if support['type'] != 'BD':
                name_doc =  get_general_document(support['date'], support['title'], support['dependence'], support['people'], support['name'], support['code'], support['hours'][0], support['hours'][1], support['type'])
                msg = upload_to_folder(name_doc, support['type'],credentials)
                # enviamos el correo con el soporte por si acaso
                sendEmialEvent(support['date'],support['hours'],calendar['emails'],support['type'],name_doc)    
                return JsonResponse({'ok': True,'message': msg, 'nameFile': name_doc})
            
            sendEmialEvent(support['date'],support['hours'],calendar['emails'],support['type']) 
            return JsonResponse({'ok': True, 'message': 'Evento agendado'})
        
        return JsonResponse({'ok': False,'message': '¡Ocurrio un error!'}); service.close()
    except jwt.exceptions.ExpiredSignatureError:
        return JsonResponse({'ok': False,'message': '!El evento no se pudo agendar¡'});
    finally:
        service.close()

#Función para devolver el formato en caso de que se haya generado. 
@csrf_exempt
@require_http_methods(['POST'])
def download_document(request):
    body = json.loads(request.body.decode('utf-8')) 
    name = body['name']
    typeEvent = body['type']
    filename = f'BECL_PDB/doc/doc_auditorio_pdf/{name}' if typeEvent == 'A' else f'BECL_PDB/doc/doc_semillero_pdf/{name}'
    fullpath = os.path.join(filename) 
    if os.path.exists(fullpath):
        # response = FileResponse(open(fullpath, 'rb'), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response = FileResponse(open(fullpath, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{name}"'
        return response
    else:
        return JsonResponse({'ok': False, 'msg':'El documento no existe.'})
    
def sendEmialEvent(day, hours, email, type, doc=''):
    
    context = {
        'day': day,
        'hour': hours
    }

    subjects = subject(type)

    html_template = render_to_string(subjects[1], context)
    text_template = strip_tags(html_template)
    #Creo un objeto EmailMultiAlternatives para enviar el correo electronico
    mail = EmailMultiAlternatives(
        subjects[0],
        text_template,
        'andresalexanderss@ufps.edu.co',
        email
    )

    #se adjunta el archivo
    if(type == 'S' or type == 'A'):
        pathDoc = f'BECL_PDB/doc/doc_semillero_pdf/{doc}' if type == 'S' else f'BECL_PDB/doc/doc_auditorio_pdf/{doc}'
        with open(pathDoc, 'rb') as f:
            mail.attach('soporte-prestamo.pdf', f.read(), 'application/pdf')

    #Agrego la plantilla HTML como un contenido alternativo al correo electronico
    mail.attach_alternative(html_template, 'text/html')
    mail.send()


def subject(type):
    subjects = {
        'A': ['Préstamo Auditorio', 'plantilla_auditorio.html'],
        'S': ['Préstamo Sala de Semilleros', 'plantilla_semillero.html'],
        'BD': ['Capacitación Base de Datos.', 'plantilla_capacitacion.html']
    }
    return subjects[type]
    


def get_general_document(date,title,dependece, people, name, code, start, end, typeEvent):
    # Se genera el documento dependiendo del typeEvent
    doc = DocxTemplate('BECL_PDB/doc/formato auditorio.docx') if  typeEvent == 'A' else DocxTemplate('BECL_PDB/doc/formato semilleros.docx')
    # titulo y semillero pueden ser lo mismo. De igual manera con el departamento y dependencia. 
    data_docx = {
        'fecha': date,
        'titulo': title,
        'dependencia': dependece ,
        'personas': people,
        'nombre': name,
        'codigo': code,
        'inicio': start,
        'fin': end,
    }
    # se genera la terminacion del formato.
    loan = 'formato-auditorio' if typeEvent == 'A' else 'formato-semillero'
    name_file = f'{date}-{code}-{title}-{loan}'
    folder = f'BECL_PDB/doc/doc_auditorio/{name_file}.docx' if typeEvent == 'A' else f'BECL_PDB/doc/doc_semillero/{name_file}.docx'
    folderPDf = f'BECL_PDB/doc/doc_auditorio_pdf/{name_file}.pdf' if typeEvent == 'A' else f'BECL_PDB/doc/doc_semillero_pdf/{name_file}.pdf'
    # se renderiza y guarda la data en el documento. 
    doc.render(data_docx)
    doc.save(folder)
    convert(folder,  folderPDf)

    return f'{name_file}.pdf'

#Funcion que me retorna el formato en el cual tengo que mandar el evento a agendar
def format_event(title,dates,emails):
    list_emails = get_list_emails(emails)
    start = dates[0]
    end = dates[1]
    event = {
        'summary': f'{title}',
        'location': '',
        'description': '',
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
def upload_to_folder(name_docx, option, credentials):
    load_dotenv()
    hour = datetime.utcnow().strftime('%H-%M-%S')
    try:
        service = build('drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': f'{hour}-{name_docx}',
            'parents': [os.getenv('FOLDER_ID_A') if option == 'A' else os.getenv('FOLDER_ID_S')]
        }
        path = f'BECL_PDB/doc/doc_auditorio/{name_docx[0:-4]}.docx' if option == 'A' else f'BECL_PDB/doc/doc_semillero/{name_docx[0:-4]}.docx'
        media = MediaFileUpload(path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document', resumable=True) 
        service.files().create(body=file_metadata, media_body=media, fields= 'id').execute()
        service.close()
        return "Se subio el archivo de manera correcta."
    except HttpError:
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
    list_events = realization_events(list_events)
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
        start_time =  datetime.strptime( datetime.fromisoformat(start).strftime('%I:%M %p'), '%I:%M %p' ).strftime('%H')
        end_time =  datetime.strptime( datetime.fromisoformat(end).strftime('%I:%M %p'), '%I:%M %p' ).strftime('%H')
        list_hours_events.append([int(start_time),int(end_time)])
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

#Funcion que filtar los eventos por la opciones: A: Auditorio, S: semillero, BD: Base de datos
def filterByOption(events,option):
    return filter(lambda event: option in event['summary'].split(':')[0] , events)


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