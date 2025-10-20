from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portada.urls')),
    path('inmuebles/', include('inmuebles.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # login
    path('accounts/login/',  auth_views.LoginView.as_view(),  name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
