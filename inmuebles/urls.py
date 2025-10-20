from django.urls import path
from . import views

app_name = "inmuebles"

urlpatterns = [
    path("", views.InmuebleList.as_view(), name="lista"),
    path("nuevo/", views.InmuebleCreate.as_view(), name="nuevo"),
    path("<int:pk>/editar/", views.InmuebleUpdate.as_view(), name="editar"),
    path("<int:pk>/borrar/", views.InmuebleDelete.as_view(), name="borrar"),
]
