from django.db.models import Q
from rest_framework import serializers
from BECL_PDB.models import Eventos
from BECL_Login.models import Usuarios


class UsuariosSerializers(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ["id", "username", "first_name", "last_name"]


class EventosSerializers(serializers.ModelSerializer):
    usuario = UsuariosSerializers()
    funcionarios = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()

    def get_estado(self, obj):
        return obj.estado.descripcion

    def get_funcionarios(self, obj):
        type_event = obj.tipo
        if type_event == "BD":
            # Lógica para obtener managers para tipo DB
            managers = Usuarios.objects.filter(ubicacion_id=3)
        else:
            # Lógica para obtener managers para otros tipos de evento
            managers = (
                Usuarios.objects.filter(ubicacion_id=1)
                if type_event == "A"
                else Usuarios.objects.filter(ubicacion_id=2)
            )

        # Serializa los managers utilizando el serializer de Usuario
        serializer = UsuariosSerializers(managers, many=True)
        return serializer.data

    class Meta:
        model = Eventos
        fields = [
            "id",
            "fecha_solicitud",
            "fecha_solicitada",
            "dependencia",
            "inicio",
            "final",
            "titulo",
            "cantidad_personas",
            "tipo",
            "encargados",
            "estado",
            "usuario",
            "funcionarios",
        ]
