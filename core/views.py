from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
import json

from .models import Poliza, Comision


def dashboard(request):

    # 💰 ingresos reales (solo pagadas)
    ingresos_totales = Comision.objects.filter(
        estado='pagada'
    ).aggregate(total=Sum('importe'))['total'] or 0

    # ⏳ pendientes
    pendientes = Comision.objects.filter(
        estado='pendiente'
    ).aggregate(total=Sum('importe'))['total'] or 0

    # 📄 pólizas activas (simple)
    polizas_activas = Poliza.objects.count()

    # 📊 ingreso medio
    ingreso_medio = Comision.objects.aggregate(avg=Avg('importe'))['avg'] or 0

    # 📈 evolución mensual
    mensual = Comision.objects.annotate(
        mes=TruncMonth('fecha_creacion')
    ).values('mes').annotate(
        total=Sum('importe')
    ).order_by('mes')

    meses = [x['mes'].strftime('%Y-%m') for x in mensual if x['mes']]
    valores_mes = [float(x['total']) for x in mensual if x['mes']]

    # 📊 por tipo póliza
    por_tipo = Poliza.objects.values('tipo').annotate(
        total=Count('id')
    )

    tipos_labels = [x['tipo'] for x in por_tipo]
    tipos_values = [x['total'] for x in por_tipo]

    # 🧑‍💼 top agentes
    top_agentes = Comision.objects.values(
        'poliza__agente__nombre'
    ).annotate(
        total=Sum('importe')
    ).order_by('-total')[:5]

    # ⏳ vencimientos próximos (30 días)
    hoy = date.today()
    proximas = Poliza.objects.filter(
        fecha_vencimiento__lte=hoy + timedelta(days=30),
        fecha_vencimiento__gte=hoy
    )

    return render(request, 'core/dashboard.html', {
        # KPIs
        'ingresos_totales': ingresos_totales,
        'pendientes': pendientes,
        'polizas_activas': polizas_activas,
        'ingreso_medio': ingreso_medio,

        # charts
        'meses': json.dumps(meses),
        'valores_mes': json.dumps(valores_mes),
        'tipos_labels': json.dumps(tipos_labels),
        'tipos_values': json.dumps(tipos_values),

        # business
        'top_agentes': top_agentes,
        'proximas': proximas,
    })