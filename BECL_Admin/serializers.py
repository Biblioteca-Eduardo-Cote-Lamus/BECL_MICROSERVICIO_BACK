from rest_framework import serializers
from BECL_PDB.models import Eventos

class EventosSerializers(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()

    def get_nombre(self, obj):
        return obj.usuario.last_name
    
    class Meta:
        model = Eventos
        fields = '__all__'
    