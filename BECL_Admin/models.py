from django.db import models

# Create your models here.
class Estado(models.Model):
    por_revisar = models.BooleanField(default=False)
    aceptado = models.BooleanField(default=False)
    rechazado = models.BooleanField(default=False)