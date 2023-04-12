from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    codigo = models.CharField(max_length=10,primary_key=True)
    nombre = models.CharField(max_length=200)
    facultad = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    usuario = models.CharField(max_length=20)
    password = models.CharField(max_length=300)
    
    def password_encript(self):
        password_nueva = make_password(self.password)
        self.password = password_nueva
    
    def password_check(self, password):
        is_valid = check_password(password, self.password)
        return is_valid
    
    def __str__(self):
        return self.username + ":" + self.password 