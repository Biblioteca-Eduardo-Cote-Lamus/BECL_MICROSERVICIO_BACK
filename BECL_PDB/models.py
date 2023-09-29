from django.db import models
from BECL_Login.models import Usuarios
from BECL_Admin.models import EstadoEvento

class Eventos(models.Model):
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_solicitada = models.CharField(max_length=50)
    dependencia = models.CharField(max_length=150)
    inicio = models.CharField(max_length=20)
    final = models.CharField(max_length=20)
    titulo = models.CharField(max_length=150)
    cantidad_personas = models.IntegerField()
    tipo = models.CharField(max_length=10)
    encargados = models.TextField(blank=True, null=True)
    mensaje_usuario = models.TextField(default='Sin comentario y/o peticiones' ,blank=True, null=True )
    url_formato = models.CharField(blank=True, null=True,max_length=255, default='Without url format yet.')
    realizado = models.BooleanField(default=False)
    rechazo_mensaje = models.TextField(default='', null=True)
    observaciones_funcionario = models.TextField(default='Sin observaciones por parte del funcionario')
    estado = models.ForeignKey(EstadoEvento, on_delete=models.CASCADE, related_name="estado_actual")
    funcionario_encargado = models.ForeignKey(Usuarios, on_delete=models.CASCADE,  related_name="encargado", null=True, default=None)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, default=None)
    class Meta:
        db_table = 'Eventos'