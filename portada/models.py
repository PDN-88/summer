from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Propietario(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank= True)
    email = models.EmailField(max_length=100, blank=True)
    direccion = models.CharField(max_length=100, blank = True)
    #codigo postal =

    def __str__(self):
        return f"{self.nombre} ({self.dni})"
    
    def num_inmuebles(self):
        return self.inmuebles.count()  # ← gracias a related_name en Inmueble
    num_inmuebles.short_description = "Nº inmuebles"


class Inmueble(models.Model):
    TIPO_CHOICES =[
        ('piso', 'Piso'),
        ('local', 'Local'),
        ('garaje', 'Garage'),
        ('trastero', 'Trastero'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    direccion = models.CharField(max_length=200)
    planta = models.CharField(max_length=10, blank=True)
    puerta = models.CharField(max_length=10, blank=True)
    metros = models.FloatField()
    habitaciones = models.IntegerField(null=True, blank=True)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='inmuebles')

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.direccion}{self.planta or ''}{self.puerta or ''}".strip()

class Inquilino(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, blank=False, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    inmueble = models.ForeignKey(Inmueble, on_delete=models.PROTECT, related_name='inquilinos', null=True,blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.dni})"

class Contrato(models.Model):
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name="contratos")
    inquilinos = models.ManyToManyField(Inquilino, related_name='contratos')
    fecha_inicio= models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    condiciones = models.TextField(blank=True)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='contratos')

    def __str__(self):
        fin = self.fecha_fin.strftime("%Y-%m-%d") if self.fecha_fin else "abierto"
        return f"{self.inmueble} · {self.fecha_inicio:%Y-%m-%d}→{fin}"
    
   

class Incidencia (models.Model):
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name='Incidencias')
    descripcion = models.TextField()
    estado = models.CharField(max_length=50, default='pendiente')
    fecha_reporte = models.DateField(auto_now_add=True)
    fecha_resolucion = models.DateField(null = True, blank=True)

    def __str__(self):
        return f"{self.inmueble} · {self.estado} · {self.fecha_reporte:%Y-%m-%d}"

class Documento(models.Model):
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name='documentos')
    descripcion = models.CharField(max_length=200, blank=True)
    archivo = models.FileField(upload_to='documentos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descripcion or self.archivo.name

class TipoPago(models.Model):
    QUIEN_CHOICES = [
        ('inquilino', 'Inquilino'),
        ('propietario', 'Propietario'),
    ]
    nombre = models.CharField(max_length=100) #ej. renta, luz, seguro
    descripcion = models.TextField(blank=True)
    quien_por_defecto = models.CharField(max_length=20, choices=QUIEN_CHOICES,blank=True)
    activo = models.BooleanField(default=True)

    #auditoria
    creado_por = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='tipospago_creados'
    )
    actualizado_por = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='tipospago_actualizados'
    )
    creado_en = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    actualizado_en = models.DateTimeField(auto_now=True,blank=True, null=True)
    #fin auditoria
    def __str__(self):
        return self.nombre

class Pago(models.Model):
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name='pagos')
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')

    tipo= models.ForeignKey(TipoPago, on_delete= models.PROTECT, related_name='pagos')

    fecha= models.DateField()
    descripcion= models.CharField(max_length=200, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    pagado = models.BooleanField(default=False)

    QUIEN_CHOICES = [
        ('inquilino', 'Inquilino'),
        ('propietario', 'Propietario'),
    ]
    quien_paga = models.CharField(max_length=20 , choices = QUIEN_CHOICES)
    
    def __str__(self):
        estado = "Pagado" if self.pagado else "Pendiente"
        return f"{self.tipo} · {self.total}€ · {estado} · {self.fecha:%Y-%m-%d}"
