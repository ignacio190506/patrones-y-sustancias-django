from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("grafico1", views.grafico1, name="grafico1"),
    path("grafico2", views.grafico2, name="grafico2"),
    path("grafico3", views.grafico3, name="grafico3"),
    path("grafico4", views.grafico4, name="grafico4"),
    path("grafico5", views.grafico5, name="grafico5"),
    path("grafico6", views.grafico6, name="grafico6"),
    path("grafico7", views.grafico7, name="grafico7"),

    # <int:numero> captura el número del reporte: /dashboard/reporte1 ... /dashboard/reporte4
    path("reporte<int:numero>", views.reporte, name="reporte"),
    path("reporte<int:numero>/pdf", views.reporte_pdf, name="reporte_pdf"),
    path("reporte<int:numero>/excel", views.reporte_excel, name="reporte_excel"),
]
