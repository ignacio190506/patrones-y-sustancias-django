from django.urls import path
from . import views


# Rutas internas de la aplicación dashboard
urlpatterns = [
    path("", views.index, name="index"),

    # Gráficos (sin barra final, como en las guías 4, 5 y 6)
    path("grafico1", views.grafico1, name="grafico1"),
    path("grafico2", views.grafico2, name="grafico2"),
    path("grafico3", views.grafico3, name="grafico3"),
    path("grafico4", views.grafico4, name="grafico4"),
    path("grafico5", views.grafico5, name="grafico5"),
    path("grafico6", views.grafico6, name="grafico6"),

    # Listados de datos en tablas
    path("listado1", views.listado1, name="listado1"),
    path("listado2", views.listado2, name="listado2"),
    path("listado3", views.listado3, name="listado3"),

    # Reportes (solo lectura)
    path("reportes/", views.reporte_lista, name="reporte_lista"),
]
