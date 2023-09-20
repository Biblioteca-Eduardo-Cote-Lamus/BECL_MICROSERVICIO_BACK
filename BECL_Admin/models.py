from django.db import models

# Create your models here.
class Estado(models.Model):
    descripcion = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'estado_evento'
    
    def __str__(self):
        return self.descripcion