# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Planta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_cientifico = models.CharField(max_length=255)
    nombre_comun = models.CharField(max_length=255, blank=True, null=True)
    #Guarda la ruta de la imagen, no existe el tipo de dato imagen en mysql
    imagen = models.CharField(max_length=255, blank=True, null=True) 
    descripcion = models.TextField(blank=True, null=True)
    cuidados = models.TextField(blank=True, null=True)

    def imagen_url(self):
        # Construye la URL completa a partir de la ruta relativa almacenada en la base de datos
        return f"/static/{self.imagen}"

    def __str__(self):
        return self.nombre_cientifico
    
class Bitacora(models.Model):
    planta = models.ForeignKey(Planta, on_delete=models.CASCADE)
    fecha = models.DateField()
    imagen = models.ImageField(upload_to='static/img/bitacora/')
    # Puedes agregar más campos si es necesario

    def __str__(self):
        return f"Bitácora de {self.planta.nombre_cientifico} - {self.fecha}"
