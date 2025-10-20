from django.urls import path
from . import views

app_name = 'portada'
urlpatterns = [
    path('', views.home, name='home'),
]
