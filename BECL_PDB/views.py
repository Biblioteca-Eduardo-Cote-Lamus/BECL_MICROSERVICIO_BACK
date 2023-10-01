from django.http import  HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from BECL_Login.utils.sendEmails import send_email
from BECL_Login.models import Usuarios
from BECL_PDB.utils.calendar import get_events_today
from BECL_Admin.models import EstadoEvento
from .models import Eventos

import os
import os.path

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
