from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from googleapiclient.discovery import build

from .serializers import EventosSerializers
from BECL_PDB.views import  getCredentials, upload_to_folder
from BECL_PDB.models import Eventos
from BECL_PDB.utils.formats import format_event, get_general_document
from BECL_Login.utils.sendEmails import send_email, SUBJECTS

class ListEvents(APIView):
    def get(self, request):
        filterId = request.data.get("filterId")
        if filterId is None:
            filterId = 1
        event_serializers = EventosSerializers(
            Eventos.objects.filter(estado_id=filterId), many=True
        )
        return Response(event_serializers.data)

class ApproveEvent(APIView):
    def put(self, request):
        id_event = int(request.data.get("id_event"))
        credentials = getCredentials()
        service = build("calendar", "v3", credentials=credentials)
        try:
            event = Eventos.objects.get(id=id_event)
            event.estado_id = 2

            # se genera el formato del evento para google drive. Se extrae el titulo, fechas (Inicio y Fin), emails y el tipo de evento.
            calendar_event = format_event(
                event.titulo,
                event.fecha_solicitada,
                event.inicio,
                event.final,
                eval(event.encargados),
            )

            # se obtiene los datos necesarios para enviar el email
            email = self.__email_data(event)

            # Generamos el doc de soporte del prestamo si el tipo del evento no es base de datos.
            name_doc = (
                None
                if event.tipo == "DB"
                else get_general_document(
                    event.fecha_solicitada,
                    event.titulo,
                    event.dependencia,
                    event.cantidad_personas,
                    event.usuario.last_name,
                    event.usuario.username,
                    event.inicio,
                    event.final,
                    event.tipo,
                )
            )

            # Guardamos en una carpeta de drive el soporte
            if event.tipo != "DB":
                upload_to_folder(name_doc, event.tipo, credentials)

            # se obtiene la ruta absoluta del documento a subir 
            # TODO: se debe de mejorar esta forma. Agregar algun ID unico a cada doc.
            # TODO: Unificar las rutas para simplificar la logica.
            files = (
                None
                if event.tipo == "DB"
                else f"{self.__get_absolute_path(event.tipo)}{name_doc}.docx"
            )

            send_email(
                data={
                    "subject": email["subject"],
                    "from": "pruebasbeclpbd@gmail.com",
                    "to": event.usuario.email,
                },
                html_template=email["template"],
                files=[files],
            )

            event.save()
            service.events().insert(calendarId="primary", body=calendar_event).execute()
            service.close()

            return Response(
                {"ok": True, "message": "Evento aceptado y agendado"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            event.estado_id = 1
            event.save()
            service.close()
            return Response(
                {"ok": False, "message": "unexpected error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def __email_data(self, event):
        template_subject = SUBJECTS[event.tipo]
        html_template = render_to_string(
            template_subject[1],
            {"day": event.fecha_solicitada, "hour": [event.inicio, event.final]},
        )
        return {"subject": template_subject[0], "template": html_template}

    def __get_absolute_path(self, typeEvent):
        return (
            "BECL_PDB/doc/doc_semillero/"
            if typeEvent == "S"
            else "BECL_PDB/doc/doc_auditorio/"
        )
