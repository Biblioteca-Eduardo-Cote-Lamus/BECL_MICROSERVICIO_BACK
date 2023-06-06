from django.db import models
from BECL_Login.models import Usuarios
from BECL_Admin.models import Estado

class Eventos(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=False, blank=False, related_name="users_event")
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=False, blank=False, related_name="state_event")
    fecha = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    dependencia = models.CharField(max_length=150)
    inicio = models.CharField(max_length=20)
    final = models.CharField(max_length=20)
    titulo = models.CharField(max_length=150)
    cantidad_personas = models.IntegerField()
    tipo = models.CharField(max_length=10)
    encargados = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    url_formato = models.CharField(blank=True, max_length=150)