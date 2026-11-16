from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    # La raíz del sitio lleva directo al dashboard
    path("", RedirectView.as_view(url="/dashboard/")),
]
