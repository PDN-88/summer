from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('', views.PagoList.as_view(), name='lista'),
    path('nuevo/', views.PagoCreate.as_view(), name='nuevo'),
    path('<int:pk>/editar/', views.PagoUpdate.as_view(), name='editar'),
    path('<int:pk>/borrar/', views.PagoDelete.as_view(), name='borrar'),
    path('<int:pk>/toggle/', views.PagoTogglePagado.as_view(), name='toggle'),
]
