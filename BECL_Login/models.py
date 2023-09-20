from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser

class Rol_Usuario(models.Model):
    descripcion = models.CharField(max_length=100, null=True)
    
    class Meta:
        db_table = 'rol_usuario'
    
    def __str__(self):
        return self.descripcion

class Usuarios (models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=150)
    facultad = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    rol = models.ForeignKey(Rol_Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name="rol_usuario")
    usuario = models.CharField(max_length=20)
    password = models.CharField(max_length=300)


    class Meta:
        db_table = 'usuarios'
    
    
    def set_password(self, password):
        self.password = password
        
    def password_encript(self, password):
        password_nueva = make_password(password)
        self.password = password_nueva
    
    def password_check(self, password):
        is_valid = check_password(password, self.password)
        return is_valid
    
    def __str__(self):
        return self.usuario