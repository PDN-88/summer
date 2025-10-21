# inmuebles/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django import forms
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.urls import reverse
from django.db.models import Exists, OuterRef, Q, Sum
from portada.models import Inmueble, Contrato, Pago, TipoPago  # usamos los modelos de 'portada'

class InmuebleList(LoginRequiredMixin, ListView):
    model = Inmueble
    template_name = 'inmuebles/lista.html'
    paginate_by = 15
    ordering = ['direccion']

    # filtros ampliados: búsqueda, atributos, estado de alquiler
    def get_queryset(self):
        today = timezone.localdate()
        subq = Contrato.objects.filter(
            inmueble=OuterRef('pk'),
            fecha_inicio__lte=today
        ).filter(Q(fecha_fin__gte=today) | Q(fecha_fin__isnull=True))

        qs = Inmueble.objects.select_related('propietario').annotate(
            alquilado=Exists(subq)
        )

        GET = self.request.GET
        q       = GET.get('q')
        tipo    = GET.get('tipo')
        prop    = GET.get('prop')
        planta  = GET.get('planta')
        m2_min  = GET.get('m2_min')
        m2_max  = GET.get('m2_max')
        hab_min = GET.get('hab_min')
        hab_max = GET.get('hab_max')
        alquilado_filtro = GET.get('alquilado')
        orden   = GET.get('orden')

        if q: qs = qs.filter(direccion__icontains=q)
        if tipo: qs = qs.filter(tipo=tipo)
        if prop: qs = qs.filter(propietario__nombre__icontains=prop)
        if planta: qs = qs.filter(planta=planta)

        if alquilado_filtro == 'si':
            qs = qs.filter(alquilado=True)
        elif alquilado_filtro == 'no':
            qs = qs.filter(alquilado=False)

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
            'alquilado': GET.get('alquilado',''),
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
    template_name = 'inmuebles/confirm_borrar.html'
    success_url = reverse_lazy('inmuebles:lista')

# ----- GESTIÓN DE PAGOS -----
class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['inmueble', 'tipo', 'fecha', 'descripcion', 'total', 'pagado', 'quien_paga']

class PagoList(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'pagos/lista.html'
    paginate_by = 20
    ordering = ['-fecha']

    def get_queryset(self):
        qs = Pago.objects.select_related('inmueble', 'tipo')
        GET = self.request.GET
        q = GET.get('q')
        inmueble_id = GET.get('inmueble')
        inmueble_q = GET.get('inmueble_q')
        tipo = GET.get('tipo')
        pagado = GET.get('pagado')
        quien = GET.get('quien')
        desde = GET.get('desde')
        hasta = GET.get('hasta')
        orden = GET.get('orden')

        if q:
            qs = qs.filter(descripcion__icontains=q)
        if inmueble_id:
            try:
                qs = qs.filter(inmueble_id=int(inmueble_id))
            except:
                pass
        if inmueble_q:
            qs = qs.filter(inmueble__direccion__icontains=inmueble_q)
        if tipo:
            try:
                qs = qs.filter(tipo_id=int(tipo))
            except:
                qs = qs.none()
        if pagado == 'si':
            qs = qs.filter(pagado=True)
        elif pagado == 'no':
            qs = qs.filter(pagado=False)
        if quien in ('inquilino','propietario'):
            qs = qs.filter(quien_paga=quien)
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)

        if orden in ('fecha','-fecha','total','-total'):
            qs = qs.order_by(orden)
        else:
            qs = qs.order_by(*self.ordering)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        GET = self.request.GET
        qs = ctx['object_list']
        totales = qs.aggregate(total=Sum('total'))
        total_pagado = qs.filter(pagado=True).aggregate(total=Sum('total'))['total'] or 0
        total_pendiente = qs.filter(pagado=False).aggregate(total=Sum('total'))['total'] or 0
        ctx.update({
            'q': GET.get('q',''),
            'inmueble': GET.get('inmueble',''),
            'inmueble_q': GET.get('inmueble_q',''),
            'tipo': GET.get('tipo',''),
            'pagado': GET.get('pagado',''),
            'quien': GET.get('quien',''),
            'desde': GET.get('desde',''),
            'hasta': GET.get('hasta',''),
            'orden': GET.get('orden','-fecha'),
            'TIPOS': TipoPago.objects.filter(activo=True).order_by('nombre'),
            'QUIEN_CHOICES': Pago.QUIEN_CHOICES,
            'total_listado': totales['total'] or 0,
            'total_pagado': total_pagado,
            'total_pendiente': total_pendiente,
            'qs_base': '&'.join(f'{k}={v}' for k,v in GET.items() if k!='page' and v!=''),
        })
        return ctx

class PagoCreate(LoginRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/form.html'
    success_url = reverse_lazy('pagos:lista')

    def get_initial(self):
        initial = super().get_initial()
        inmueble = self.request.GET.get('inmueble')
        tipo_id = self.request.GET.get('tipo')
        if inmueble:
            try:
                initial['inmueble'] = int(inmueble)
            except:
                pass
        if tipo_id:
            try:
                t = TipoPago.objects.get(pk=int(tipo_id))
                if t.quien_por_defecto:
                    initial['quien_paga'] = t.quien_por_defecto
            except TipoPago.DoesNotExist:
                pass
        initial.setdefault('fecha', timezone.localdate())
        return initial

    def form_valid(self, form):
        # autoasociar contrato activo
        inmueble = form.cleaned_data.get('inmueble')
        fecha = form.cleaned_data.get('fecha') or timezone.localdate()
        contrato_activo = Contrato.objects.filter(
            inmueble=inmueble,
            fecha_inicio__lte=fecha
        ).filter(Q(fecha_fin__gte=fecha) | Q(fecha_fin__isnull=True)).order_by('-fecha_inicio').first()
        if contrato_activo:
            form.instance.contrato = contrato_activo
        return super().form_valid(form)

class PagoUpdate(LoginRequiredMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/form.html'
    success_url = reverse_lazy('pagos:lista')

class PagoDelete(LoginRequiredMixin, DeleteView):
    model = Pago
    template_name = 'pagos/confirm_borrar.html'
    success_url = reverse_lazy('pagos:lista')

class PagoTogglePagado(LoginRequiredMixin, View):
    def post(self, request, pk):
        pago = get_object_or_404(Pago, pk=pk)
        pago.pagado = not pago.pagado
        pago.save(update_fields=['pagado'])
        next_url = request.POST.get('next') or reverse('pagos:lista')
        return redirect(next_url)
