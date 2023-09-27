from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser

class UbicacionFuncionario(models.Model):
    descripcion = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'ubicacion_funcionario'

class CargoUsuario(models.Model):
    descripcion = models.CharField(max_length=100, null=True)
    
    class Meta:
        db_table = 'cargo_usuario'
    
    def __str__(self):
        return self.descripcion

class Usuarios (AbstractUser):
    facultad = models.CharField(max_length=150)
    cargo = models.ForeignKey(CargoUsuario, on_delete=models.CASCADE, null=True, blank=True, related_name="cargo_usuario")
    ubicacion = models.ForeignKey(UbicacionFuncionario, on_delete=models.CASCADE, null=True, blank=True, related_name="ubicacion")
    class Meta:
        db_table = 'usuarios'