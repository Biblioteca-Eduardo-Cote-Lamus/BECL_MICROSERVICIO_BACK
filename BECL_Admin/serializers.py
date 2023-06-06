from rest_framework import serializers
from BECL_PDB.models import Eventos

class EventosSerializers(serializers.ModelSerializer):
    class Meta:
        model = Eventos
        fields = '__all__'
    