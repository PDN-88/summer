# inmuebles/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from portada.models import Inmueble  # usamos el modelo de 'portada'

class InmuebleList(LoginRequiredMixin, ListView):
    model = Inmueble
    template_name = 'inmuebles/lista.html'
    paginate_by = 15
    ordering = ['direccion']

    # filtros básicos ampliables
    def get_queryset(self):
        qs = Inmueble.objects.select_related('propietario')
        GET = self.request.GET
        q       = GET.get('q')
        tipo    = GET.get('tipo')
        prop    = GET.get('prop')
        planta  = GET.get('planta')
        m2_min  = GET.get('m2_min')
        m2_max  = GET.get('m2_max')
        hab_min = GET.get('hab_min')
        hab_max = GET.get('hab_max')
        orden   = GET.get('orden')

        if q: qs = qs.filter(direccion__icontains=q)
        if tipo: qs = qs.filter(tipo=tipo)
        if prop: qs = qs.filter(propietario__nombre__icontains=prop)
        if planta: qs = qs.filter(planta=planta)

        def to_float(v):
            try: return float(v)
            except: return None
        def to_int(v):
            try: return int(v)
            except: return None

        m2_min_v, m2_max_v = to_float(m2_min), to_float(m2_max)
        hab_min_v, hab_max_v = to_int(hab_min), to_int(hab_max)

        if m2_min_v is not None: qs = qs.filter(metros__gte=m2_min_v)
        if m2_max_v is not None: qs = qs.filter(metros__lte=m2_max_v)
        if hab_min_v is not None: qs = qs.filter(habitaciones__gte=hab_min_v)
        if hab_max_v is not None: qs = qs.filter(habitaciones__lte=hab_max_v)

        if orden in ('direccion','-direccion','metros','-metros','habitaciones','-habitaciones'):
            qs = qs.order_by(orden)
        else:
            qs = qs.order_by(*self.ordering)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        GET = self.request.GET
        ctx.update({
            'q': GET.get('q',''),
            'tipo': GET.get('tipo',''),
            'prop': GET.get('prop',''),
            'planta': GET.get('planta',''),
            'm2_min': GET.get('m2_min',''),
            'm2_max': GET.get('m2_max',''),
            'hab_min': GET.get('hab_min',''),
            'hab_max': GET.get('hab_max',''),
            'orden': GET.get('orden','-direccion'),
            'TIPO_CHOICES': Inmueble.TIPO_CHOICES,
            'qs_base': '&'.join(f'{k}={v}' for k,v in GET.items() if k!='page' and v!=''),
        })
        return ctx

class InmuebleCreate(LoginRequiredMixin, CreateView):
    model = Inmueble
    fields = ['tipo','direccion','planta','puerta','metros','habitaciones','propietario']
    template_name = 'inmuebles/form.html'
    success_url = reverse_lazy('inmuebles:lista')

class InmuebleUpdate(LoginRequiredMixin, UpdateView):
    model = Inmueble
    fields = ['tipo','direccion','planta','puerta','metros','habitaciones','propietario']
    template_name = 'inmuebles/form.html'
    success_url = reverse_lazy('inmuebles:lista')

class InmuebleDelete(LoginRequiredMixin, DeleteView):
    model = Inmueble
    template_name = 'inmuebles/confirm_delete.html'
    success_url = reverse_lazy('inmuebles:lista')
