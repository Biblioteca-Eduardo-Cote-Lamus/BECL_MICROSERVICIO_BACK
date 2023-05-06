from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuarios (models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=150)
    facultad = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    usuario = models.CharField(max_length=20)
    password = models.CharField(max_length=300)
    
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