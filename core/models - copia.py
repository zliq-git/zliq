from django.db import models
from django.conf import settings


# 🏢 AGENCIA
class Agencia(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


# 👤 AGENTE
class Agente(models.Model):
    agencia = models.ForeignKey(Agencia, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


# 📄 PÓLIZA
class Poliza(models.Model):

    TIPO_POLIZA_CHOICES = [
        ('auto', 'Auto'),
        ('vida', 'Vida'),
        ('salud', 'Salud'),
        ('hogar', 'Hogar'),
        ('otros', 'Otros'),
    ]

    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    numero_poliza = models.CharField(max_length=50, unique=True)
    cliente = models.CharField(max_length=255)
    prima_neta = models.DecimalField(max_digits=10, decimal_places=2)
    recargos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    porcentaje_comision = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_POLIZA_CHOICES,
        default='otros'
    )

    # ✅ TODO ESTO VA DENTRO DE LA CLASE

    def __str__(self):
        return f"{self.numero_poliza} - {self.cliente}"

    def calcular_comision(self):
        return (self.prima_neta * self.porcentaje_comision) / 100

    def calcular_impuesto(self):
        return (self.prima_neta * settings.IMPUESTO_PORCENTAJE) / 100

    def calcular_prima_total(self):
        return (
            self.prima_neta +
            self.calcular_comision() +
            self.calcular_impuesto() +
            self.recargos
        )
    

    

# 📄 COMISION
class Comision(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
    ]

    poliza = models.OneToOneField('Poliza', on_delete=models.CASCADE)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.poliza.cliente} - {self.estado}"
    

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Poliza)
def crear_o_actualizar_comision(sender, instance, created, **kwargs):
    comision, creada = Comision.objects.get_or_create(
        poliza=instance,
        defaults={
            'importe': instance.calcular_comision(),
            'estado': 'pendiente'
        }
    )

    nuevo_importe = instance.calcular_comision()

    if not creada and comision.importe != nuevo_importe:
        comision.importe = nuevo_importe
        comision.save()