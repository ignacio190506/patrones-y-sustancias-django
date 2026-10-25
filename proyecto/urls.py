from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


# Rutas principales del proyecto
urlpatterns = [
    # Panel administrativo de Django
    path("admin/", admin.site.urls),

    # Rutas pertenecientes a la aplicación dashboard
    path("dashboard/", include("dashboard.urls")),

    # Abrir http://127.0.0.1:8000/ lleva directo al dashboard
    path("", RedirectView.as_view(url="/dashboard/")),
]
