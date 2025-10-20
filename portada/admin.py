from django.contrib import admin

# Register your models here.
from .models import Inmueble, Propietario, Inquilino, Contrato, Pago, TipoPago

#admin.site.register(Inmueble)
#admin.site.register(Propietario)
#admin.site.register(Inquilino)
#admin.site.register(Contrato)
#admin.site.register(Pago)
admin.site.register(TipoPago)

#Editamos menu admin

class InmuebleInline(admin.TabularInline):  # usa StackedInline si prefieres en bloques
    model = Inmueble
    extra = 0
    fields = ('tipo', 'direccion', 'planta', 'puerta', 'metros', 'habitaciones')
    show_change_link = True  # enlace a la página del inmueble

# --- Admin de Propietario con el inline ---
@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    inlines = [InmuebleInline]
    list_display = ('nombre', 'dni', 'num_inmuebles')
    search_fields = ('nombre', 'dni', 'email', 'telefono')

    def num_inmuebles(self, obj):
        return obj.inmuebles.count()
    num_inmuebles.short_description = "Nº inmuebles"

# --- Admin de Inmueble (mejoras útiles) ---
@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = ('direccion', 'tipo', 'propietario', 'metros', 'habitaciones')
    list_filter = ('tipo',)
    search_fields = ('direccion', 'propietario__nombre', 'propietario__dni')
    autocomplete_fields = ('propietario',)  # autocompletado si hay muchos propietarios

# --- Resto de modelos ---
@admin.register(Inquilino)
class InquilinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dni', 'telefono', 'email', 'inmueble')
    search_fields = ('nombre', 'dni', 'email', 'telefono', 'inmueble__direccion')
    list_filter = ('inmueble__tipo',)

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_inquilinos','get_propietario', 'inmueble')

    def get_inquilinos(self, obj):
        return ", ".join([i.nombre for i in obj.inquilinos.all()])
    get_inquilinos.short_description = "Inquilinos"

    def get_propietario(self, obj):
        return obj.inmueble.propietario.nombre if obj.inmueble and obj.inmueble.propietario else "-"
    get_propietario.short_description = "Propietario"

class TipoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'quien_por_defecto', 'activo', 'actualizado_en')
    list_filter = ('activo', 'quien_por_defecto')
    search_fields = ('nombre', 'descripcion')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'inmueble', 'total', 'pagado', 'quien_paga')
    list_filter = ('pagado', 'tipo', 'quien_paga', 'fecha')
    search_fields = ('descripcion', 'inmueble__direccion', 'tipo__nombre')