from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from BECL_Login.utils.sendEmails import send_email
from BECL_Login.models import Usuarios
from BECL_PDB.utils.calendar import get_events_today
from BECL_PDB.mixins import GoogleAPIMixin
from BECL_Admin.models import EstadoEvento
from BECL_PDB.models import Eventos


class CalendarEvents(APIView, GoogleAPIMixin):

    def post(self, request):
        self.init_service("calendar")
        # Obtengo los datos de la peticion.
        dates = request.data.get("dates")
        type_event = request.data.get("type")
        try:
            events = get_events_today(self.get_list_events(dates[0], dates[1]), type_event)
            return Response(
                {"ok": True, "events_hours": events}, status=status.HTTP_200_OK
            )
        except:
            return Response({"ok": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            self.service.close()


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

