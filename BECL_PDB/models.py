from django.db import models
from BECL_Login.models import Usuarios

# Create your models here.
class Events_P(models.Model):
    id = models.BigIntegerField(primary_key=True)
    codigo_user = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=False, blank=False, related_name="users_event")
    titulo = models.CharField(max_length=150)
    fecha = models.CharField(max_length=50)
    hora_inicio = models.CharField(max_length=20)
    hora_final = models.CharField(max_length=20)
    asistente = models.IntegerField()
    observaciones = models.TextField(blank=True)
    entrega = models.BooleanField(default=False)
    
    def __str__(self):
        return self.titulo + "," + self.fecha + "," + self.hora_inicio + "," + self.hora_final + "," + self.asistente
    

class Events_DB(models.Model):
    id = models.BigIntegerField(primary_key=True)
    codigo_user = models.ForeignKey(Usuarios, on_delete=models.CASCADE,  null=False, blank=False, related_name="users_db")
    titulo = models.CharField(max_length=150)
    fecha = models.CharField(max_length=50)
    hora_inicio = models.CharField(max_length=20)
    hora_final = models.CharField(max_length=20)
    asistente = models.IntegerField()
    
    def __str__(self):
        return self.titulo + "," + self.fecha + "," + self.hora_inicio + "," + self.hora_final + "," + self.asistente