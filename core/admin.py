from django.contrib import admin
from .models import Agencia, Agente, Poliza, Comision


@admin.register(Poliza)
class PolizaAdmin(admin.ModelAdmin):
    list_display = ('numero_poliza', 'cliente','tipo',
                     'prima_neta', 'porcentaje_comision',
                     'fecha_inicio','fecha_vencimiento', 
                     'mostrar_comision','mostrar_impuesto','mostrar_total')

    def mostrar_comision(self, obj):
        return obj.calcular_comision()
    
    def mostrar_total(self, obj):
        return obj.calcular_prima_total()
    
    def mostrar_impuesto(self, obj):
        return obj.calcular_impuesto()
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 🟢 SOLO si es creación (no edición)
        if not change:
            from .models import Comision

            Comision.objects.create(
                poliza=obj,
                importe=obj.calcular_comision(),
                estado='pendiente',
                tipo='alta',
                prima_neta_snapshot=obj.prima_neta,
                porcentaje_comision_snapshot=obj.porcentaje_comision
            )

    mostrar_impuesto.short_description = 'Impuesto (€)'
    mostrar_comision.short_description = 'Comisión (€)'
    mostrar_total.short_description = 'Prima total (€)'

    

@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ('mostrar_poliza', 'mostrar_agente', 'importe', 'estado', 'fecha_creacion')

    fields = ('poliza', 'mostrar_agente', 'importe', 'estado')
    readonly_fields = ('mostrar_agente',)

    def mostrar_poliza(self, obj):
        return f"{obj.poliza.numero_poliza} - {obj.poliza.cliente}"

    mostrar_poliza.short_description = 'Póliza'

    def mostrar_agente(self, obj):
        return obj.poliza.agente.nombre

    mostrar_agente.short_description = 'Agente'


admin.site.register(Agencia)
admin.site.register(Agente)

