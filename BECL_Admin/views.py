from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from googleapiclient.http import MediaFileUpload

from BECL_PDB.models import Eventos
from BECL_PDB.mixins import GoogleAPIMixin
from BECL_PDB.utils.formats import format_event, get_general_document
from BECL_Login.utils.sendEmails import send_email, SUBJECTS
from BECL_Admin.serializers import EventosSerializers

import uuid
import os


class ListEvents(APIView):
    def get(self, request):
        filterId = request.data.get("filterId")
        if filterId is None:
            filterId = 1
        event_serializers = EventosSerializers(
            Eventos.objects.filter(estado_id=filterId), many=True
        )
        return Response(event_serializers.data)


class ApproveEvent(APIView, GoogleAPIMixin):
    def upload_doc(self, name_docx, option):
        try:
            self.init_service("drive")
            file_metadata = {
                "name": f"{uuid.uuid4().hex}-{name_docx}",
                "parents": [
                    os.environ.get("FOLDER_A")
                    if option == "A"
                    else os.environ.get("FOLDER_S")
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
            self.service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
            return "Se subio el archivo de manera correcta."
        except Exception as e:
            raise e

    def put(self, request):
        id_event = int(request.data.get("id_event"))
        self.init_service("calendar")
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
                self.upload_doc(name_doc, event.tipo)

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
            self.init_service("calendar")
            self.insert_event(calendar_event)
            self.service.close()

            return Response(
                {"ok": True, "message": "Evento aceptado y agendado"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            event.estado_id = 1
            event.save()
            self.service.close()
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
