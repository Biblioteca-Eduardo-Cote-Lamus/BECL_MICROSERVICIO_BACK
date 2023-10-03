from rest_framework import serializers
from BECL_PDB.models import Eventos
from BECL_Login.models import Usuarios
class EventosSerializers(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()

    def get_nombre(self, obj):
        return obj.usuario.last_name
    
    class Meta:
        model = Eventos
        fields = '__all__'

class UsuariosSerializers(serializers.ModelSerializer):
    class Meta:
        model = Usuarios 
        fields = ["username","first_name","last_name"]