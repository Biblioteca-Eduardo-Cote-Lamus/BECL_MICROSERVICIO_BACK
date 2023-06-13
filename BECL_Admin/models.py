from django.db import models

# Create your models here.
class Estado(models.Model):
    descripcion = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.descripcion