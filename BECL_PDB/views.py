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
from docxtpl import DocxTemplate
from .models import Eventos
from BECL_Login.models import Usuarios
from BECL_Admin.models import EstadoEvento
import os
import os.path
import jwt

# ============================================================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .utils.calendar import get_events_today
from BECL_Login.utils.sendEmails import send_email

list_events = []
list_hours_today = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]


class CalendarEvents(APIView):
    def post(self, request):
        credentials = getCredentials()
        calendar_service = build("calendar", "v3", credentials=credentials)
        # Obtengo los datos de la peticion.
        dates = request.data.get("dates")
        type_event = request.data.get("type")
        # obtengo las horas disponibles
        hours = get_events_today(calendar_service, dates[0], dates[1], type_event)
        try:
            events = get_events_today(calendar_service, dates[0], dates[1], type_event)
            return Response(
                {"ok": True, "events_hours": events}, status=status.HTTP_200_OK
            )
        except:
            return Response({"ok": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            calendar_service.close()
class SaveEvent(APIView):
    def post(self, request):
        try:
            support = request.data.get("support")
            user = Usuarios.objects.get(username=support["code"])
            state_event = EstadoEvento.objects.get(id=1)
            event = Eventos(
                fecha_solicitada=support["date"],
                dependencia=support["dependence"],
                inicio=support["hours"][0],
                final=support["hours"][1],
                titulo=support["title"],
                cantidad_personas=support["people"],
                tipo=support["type"],
                encargados=support["managers"],
                estado=state_event,
                usuario=user,
            )
            event.save()
            # TODO: Implemented a html_template.
            send_email(
                data={
                    "subject": "Evento enviado a revision",
                    "body": "Su petición se ha enviado correctamente. Será revisa y se le notificará en caso de ser rechazada, aceptada y/o cancelada.",
                    "from": "pruebasbeclpbd@gmail.com",
                    "to": user.email,
                }
            )

            return Response(
                {"ok": True, "message": "Se ha guardado el evento"},
                status=status.HTTP_200_OK,
            )
        except:
            Eventos.objects.get(id=event.id).delete()
            return Response(
                {"ok": False, "message": "Ha ocurrido un error inesperado"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def sendEmialEvent(day, hours, email, typeE, doc=""):
    context = {"day": day, "hour": hours}

    subjects = subject(typeE)

    html_template = render_to_string(subjects[1], context)
    text_template = strip_tags(html_template)
    # Creo un objeto EmailMultiAlternatives para enviar el correo electronico
    mail = EmailMultiAlternatives(
        subjects[0], text_template, "pruebasbeclpbd@gmail.com", email
    )

    if typeE == "S" or typeE == "A":
        pathDoc = (
            f"BECL_PDB/doc/doc_semillero/{doc}.docx"
            if typeE == "S"
            else f"BECL_PDB/doc/doc_auditorio/{doc}.docx"
        )
        with open(pathDoc, "rb") as f:
            mail.attach_file(pathDoc)

    # Agrego la plantilla HTML como un contenido alternativo al correo electronico
    mail.attach_alternative(html_template, "text/html")
    mail.send()


def subject(type):
    subjects = {
        "A": ["Préstamo Auditorio", "plantilla_auditorio.html"],
        "S": ["Préstamo Sala de Semilleros", "plantilla_semillero.html"],
        "BD": ["Capacitación Base de Datos.", "plantilla_capacitacion.html"],
    }
    return subjects[type]

# Funcion que sube los formatos de prestamo a una carpeta de drive
def upload_to_folder(name_docx, option, credentials):
    hour = datetime.utcnow().strftime("%H-%M-%S")
    try:
        service = build("drive", "v3", credentials=credentials)
        file_metadata = {
            "name": f"{hour}-{name_docx}",
            "parents": [
                os.getenv("FOLDER_ID_A") if option == "A" else os.getenv("FOLDER_ID_S")
            ],
        }
        path = (
            f"BECL_PDB/doc/doc_auditorio/{name_docx}.docx"
            if option == "A"
            else f"BECL_PDB/doc/doc_semillero/{name_docx}.docx"
        )
        media = MediaFileUpload(
            path,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            resumable=True,
        )
        service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        service.close()
        return "Se subio el archivo de manera correcta."
    except HttpError:
        return HttpResponse("ocurrio un error")

# Funcion que valida que el token este activo
def is_Token_Valid(token):
    colombia_time = datetime.utcnow() + timedelta(hours=-5)
    decode_token = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
    exp_timestamp = decode_token["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    if colombia_time < exp_datetime:
        return False
    else:
        return True

# Funcion que me genera el token
def getCredentials():
    # Si modifica este scopes, borra el archivo token.json
    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = None
    # El archivo token.json almacena los tokens de acceso y actualización del usuario, y es
    # creado automáticamente cuando el flujo de autorización se completa por primera vez
    # tiempo.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # Si no hay credenciales (válidas) disponibles, permita que el usuario inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


"""
def stringToInt(list_hours):
    list_hours_int = []
    for hours in list_hours:
        start = datetime.strptime(hours[0], '%I:%M %p').strftime('%H')
        end = datetime.strptime(hours[1], '%I:%M %p').strftime('%H')
        list_hours_int.append([int(start), int(end)])
    return list_hours_int

"""

"""
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def events_PDB(request):
    credentials = getCredentials()
    body = json.loads(request.body.decode('utf-8'))
    token = body.get('token')
    date = body.get('dates')
    type_event = body.get('type')
    service = build('calendar', 'v3', credentials=credentials)
    try:
        events = get_events_today(service,date[0],date[1],type_event)
        service.close()
        return JsonResponse({'events_hours':events})     
    except:
        return JsonResponse({'ok': False})

"""

"""
@csrf_exempt
@require_http_methods(["POST"])
def schedule_PDB(request):
    body = json.loads(request.body.decode("utf-8"))
    token = request.headers.get("Authorization")
    # se extrae toda la información del parametro data que se envia de la request.
    support = body.get("data")["support"]
    try:
        if not is_Token_Valid(token):
            user = Usuarios.objects.get(codigo=support["code"])
            estado = EstadoEvento.objects.get(id=1)

            evento = Eventos(
                usuario=user,
                estado=estado,
                fecha=support["date"],
                dependencia=support["dependence"],
                inicio=support["hours"][0],
                final=support["hours"][1],
                titulo=support["title"],
                cantidad_personas=support["people"],
                tipo=support["type"],
                encargados=support["managers"],
                observaciones=support["observations"],
            )
            evento.save()
        return JsonResponse({"ok": True, "message": "Se ha guardado el evento"})
    except jwt.exceptions.ExpiredSignatureError:
        return JsonResponse({"ok": False, "message": "!El evento no se pudo agendar¡"})


"""

"""
# Función para devolver el formato en caso de que se haya generado.
@csrf_exempt
@require_http_methods(["POST"])
def download_document(request):
    body = json.loads(request.body.decode("utf-8"))
    name = body["name"]
    typeEvent = body["type"]
    filename = (
        f"BECL_PDB/doc/doc_auditorio_pdf/{name}"
        if typeEvent == "A"
        else f"BECL_PDB/doc/doc_semillero_pdf/{name}"
    )
    fullpath = os.path.join(filename)
    if os.path.exists(fullpath):
        # response = FileResponse(open(fullpath, 'rb'), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response = FileResponse(open(fullpath, "rb"), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{name}"'
        return response
    else:
        return JsonResponse({"ok": False, "msg": "El documento no existe."})
"""
