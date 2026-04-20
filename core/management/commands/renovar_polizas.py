from django.core.management.base import BaseCommand
from core.models import Poliza, Comision
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Genera comisiones por renovación automática'

    def handle(self, *args, **kwargs):
        hoy = date.today()

        self.stdout.write(f"🔥 INICIO RENOVACIÓN - HOY: {hoy}")

        polizas = Poliza.objects.filter(fecha_vencimiento__lte=hoy)

        self.stdout.write(f"📄 Pólizas encontradas con vencimiento hoy: {polizas.count()}")

        for poliza in polizas:

            self.stdout.write(f"➡️ Procesando póliza: {poliza.numero_poliza}")
            self.stdout.write(f"   Cliente: {poliza.cliente}")
            self.stdout.write(f"   Vence: {poliza.fecha_vencimiento}")

            # 🔒 Evitar duplicados
            existe = Comision.objects.filter(
                poliza=poliza,
                tipo='renovacion',                
            ).exists()

            self.stdout.write(f"   ¿Comisión ya existe?: {existe}")

            if existe:
                self.stdout.write("   ⛔ Saltando por duplicado")
                continue

            # Crear comisión
            self.stdout.write("   💰 Creando comisión...")

            Comision.objects.create(
                poliza=poliza,
                importe=poliza.calcular_comision(),
                estado='pendiente',
                tipo='renovacion',
                prima_neta_snapshot=poliza.prima_neta,
                porcentaje_comision_snapshot=poliza.porcentaje_comision
            )

            # 🔁 Renovar fecha
            if poliza.fecha_vencimiento:
                poliza.fecha_vencimiento = poliza.fecha_vencimiento + timedelta(days=365)
                poliza.save()

            self.stdout.write(f"   ✅ Renovada póliza {poliza.numero_poliza}")

        self.stdout.write("🏁 FIN DEL PROCESO")